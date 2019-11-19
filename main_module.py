from datetime import datetime
import speech_recognition as sr

from recognizer_module import recognize_from_audio, get_pauses
from tts_module import text_to_speech_espeak as tts_espeak
from tts_module import text_to_speech_rhvoice as tts_rhvoice
from tts_module import play_audio, engine

from pathlib import Path
import yaml
from answers import parse_answers, Step, Answer

from settings import MODE
from datetime import datetime, timedelta
import soundfile as sf
import json
import time


folder = 'audios/'

if MODE == 'SPEAKER':
    tts = play_audio
else:
    tts = tts_espeak


def get_words_from_speech(speech):
    if len(speech['audios']) == 0:  # silence
        return None

    res = [audio['text'].split(
        ' ') for audio in speech['audios'] if audio['text'] is not None]
    res = sum(res, [])
    return res


def get_words(stage):
    if len(stage) == 0:  # silence
        return None
    res = [speech['text'].split(' ') for speech in stage if speech['text'] is not None]
    res = sum(res, [])
    return res


def rejection(db):
    print('rejected')
    tts(db['reject'].answers[0].say)
    return 1


def later(db):
    print('later')
    tts(db['later'].answers[0].say)
    return 2


def silence(db):
    print('silence')
    tts(db['silence'].answers[0].say)
    return 3


def accept(db):
    global stage, keyword
    print('accepted')
    all_speeches.append([])
    stage += 1
    keyword = False
    tts(db[stage].answers[-1].say)
    dialog()
    return 0


def incorrect(db):
    print('incorrect')
    tts(db['incorrect'].answers[0].say)
    return 4


def end_call(text):
    print('exit')
    tts(text)
    return 0


def next_choise(command, db):
    if command == 'REJECT':
        result = rejection(db)
    elif command == 'LATER':
        result = later(db)
    elif command == 'ACCEPT':
        result = accept(db)
    elif command == 'EXIT':
        result = end_call(db[stage].answers[-1].say)
    else:
        result = 'error'
    return result


def get_answer(text, db, only_check=False):
    """
    text - list of words from user response
    db - dict with answers from yaml file
    stage - start position in file  
    """
    for answer in db[stage + 1].answers:
        for word in text:
            if word in answer.keyword:
                if only_check:
                    return True
                answer = next_choise(answer.cmd, db)
                return answer
    if only_check:
        return False
    return incorrect(db)


def dialog(answer_time=5, repeat=2):
    for attempt in range(repeat):  # repeats

        # time to answer
        for _ in range(10 * answer_time):
            if keyword:
                break
            print(_)
            time.sleep(0.1)

        text = get_words(all_speeches[stage])
        print('text in dialog:', text)
        if text is None:  # silence
            silence(db)
        elif len(text) == 0:  # not recognize
            incorrect(db)
        else:
            answer = get_answer(text, db)
            if answer == 4:
                continue
            break
        print('attempt=', attempt)
        if attempt == repeat - 1:
            later(db)


def callback(recognizer, audio):
    global keyword
    end_time = datetime.now()
    filename = "audio_{}.flac".format(end_time.strftime('%H_%M_%S'))
    flac_data = audio.get_flac_data()
    with open(folder + filename, 'wb') as f:
        f.write(flac_data)

    f = sf.SoundFile(folder + filename)
    duration = len(f) / f.samplerate
    start_time = end_time - timedelta(seconds=duration)

    text = recognize_from_audio(recognizer, audio)
    print(text)

    result = {
        # 'audio': audio,
        'start_speech': start_time,
        'end_speech': end_time,
        'duration': duration,
        'audio_filename': filename,
        'text': text,
    }
    all_speeches[stage].append(result)
    if text :
        words = text.split(' ')
        if get_answer(words, db, True):
            engine.stop()
            print('engine stopped')
            keyword = True


def format_json(start_call, end_call, all_speeches):
    json_results = []
    for index, stage in enumerate(all_speeches):
        json_results.append([])
        for speech in stage:
            res = {key: (value if not isinstance(value, datetime) else value.strftime(
                '%H_%M_%S')) for key, value in speech.items()}
            json_results[index].append(res)
        json_results[index].append({'pauses': get_pauses(stage)})

    result = {
        'start_call': start_call.strftime('%Y-%m-%d %H_%M_%S'),
        'end_call': end_call.strftime('%Y-%m-%d %H_%M_%S'),
        'duration': (end_call - start_call).total_seconds(),
        'stages': json_results
    }
    json_filename = "data_{}.json".format(result['start_call'])
    with open(json_filename, 'w') as f:
        f.write(json.dumps(result))


r = sr.Recognizer()  # Creating Recognizer object
mic = sr.Microphone()  # Creating Microphone object

data = yaml.safe_load(Path('answers.yaml').open())
db = parse_answers(data)
stage = 0
all_speeches = [[]]
keyword = False


if __name__ == "__main__":
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print('voice recording started')

    start_record = datetime.now()
    stop_listening = r.listen_in_background(source, callback)

    tts(db[0].answers[0].say)  # first phrase
    dialog(4)
    stop_listening()
    print('voice recording stopped')
    end_record = datetime.now()
    print(all_speeches)
    format_json(start_record, end_record, all_speeches)
    time.sleep(2)
