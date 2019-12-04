import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import speech_recognition as sr
import soundfile as sf
import miniaudio

from recognizer_module import recognize_from_audio
from answers import parse_answers, Step, Answer
from settings import MODE, REPEAT
import say


users_speech_folder = 'user_speeches/'

device = miniaudio.PlaybackDevice()
r = sr.Recognizer()  # Creating Recognizer object
mic = sr.Microphone()  # Creating Microphone object

db = say.parse_dialog(Path('outgoing3.txt').read_text().splitlines())
root_say_obj = db.get("root")
replies = root_say_obj.reply

stage = 0
all_speeches = [[]]
keyword = False
# end_call = False
attempt = 0


def toggle_keyword():
    global keyword
    keyword = not keyword


def get_keyword():
    global keyword
    return keyword


def callback(recognizer, audio):
    """
    This function is called in a new thread when a voice is recorded.
    Input parameters: 
    recognizer - Recognizer object from main thread
    audio - Audio object with recorded audio
    """
    global keyword, replies
    end_time = datetime.now()
    filename = "audio_{}.flac".format(end_time.strftime('%H_%M_%S'))
    flac_data = audio.get_flac_data()
    with open(users_speech_folder + filename, 'wb') as f:
        f.write(flac_data)

    f = sf.SoundFile(users_speech_folder + filename)
    duration = len(f) / f.samplerate
    start_time = end_time - timedelta(seconds=duration)

    text = recognize_from_audio(recognizer, audio)
    print(text)

    result = {
        'start_speech': start_time,
        'end_speech': end_time,
        'duration': duration,
        'audio_filename': filename,
        'text': text,
    }
    all_speeches[stage].append(result)
    if text and get_next_say(replies, [text], True):
        try:
            device.stop()
        except:
            pass
        print('engine stopped')
        toggle_keyword()


def get_pauses(results):
    """
    function return list of pause lengths
    """
    pauses = []
    if len(results) > 1:
        for index, res in enumerate(results[:-1]):
            pause = results[index + 1]["start_speech"] - res["end_speech"]
            pauses.append(pause.total_seconds())
    return pauses


def format_json(start_call, end_call, all_speeches):
    """
    function saves data to json file
    """
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


def silence(db):
    print('silence')
    # return db['silence'].answers[0].say  # 3
    return('silence')


def incorrect(db):
    print('incorrect')
    # return db['incorrect'].answers[0].say  # 4
    return "incorrect"


# def call_end(text):
#     global end_call, stage
#     end_call = True
#     print('exit', stage)
#     return db[stage + 1].answers[-1].say  # text 0


def do_command(commands):
    global replies
    print(commands)
    for command in commands:
        if command.cmd == 'goto':
            replies = db.get(command.value).reply
            # dialog(db.get(command.value), is_repeat=True)
            return 1
        else:
            return 0


def get_next_say(replies, speech, only_check=False):
    """
    function seeks words and phrases in lists and returns the appropriate command
    """
    keywords = {replies.index(
        say_o): [keyword.keyword for keyword in say_o.hear] for say_o in replies}
    for key, value in keywords.items():
        for val in value:
            if val in speech:
                if only_check:
                    return True
                return replies[key]
    return replies[-1]


def get_phrases_from_speech(stage):
    """
    Function returns list of phrases from current stage
    """
    if len(stage) == 0:  # silence
        return None
    res = [speech['text']
           for speech in stage if speech['text'] is not None]
    print(res) # for debug
    return res


def play_audio(filename):
    print(filename) # for debug
    f = sf.SoundFile(filename)
    duration = len(f) / f.samplerate
    stream = miniaudio.stream_file(filename)
    # print(duration) 
    device.start(stream)
    for _ in range(int(10 * duration) + 1):
        if get_keyword():
            break
        time.sleep(0.1)
    try:
        device.stop()
    except Exception as e:
        print(e)


def end_call(code):
    if code == 'silence':
        print('end_call')
        return 0


'''
def dialog2(say_obj, is_repeat=False, answer_time=5, repeat=2):
    """
    The function is the main logic for selecting the next phrase, recording speech, recognizing it.
    Return phrase for next step
    """
    print('is_repeat', is_repeat)
    global keyword, attempt, replies
    replies = say_obj.reply
    keyword = False

    
    if not is_repeat:
        play_audio(say_obj.say[0].audio)  # play speak_phrase from parameters
        if say_obj.cmd is not None:
            do_command(say_obj.cmd)

    if replies is None:
        return 0
    # Waiting for an answer
    print('time to answer')
    for _ in range(10 * answer_time):
        if get_keyword():
            break
        time.sleep(0.1)

    text = get_phrases_from_speech(all_speeches[stage])
    print('text in dialog:', text)  # for debug
    if text is None or len(text) == 0:  # silence
        if is_repeat:
            end_call("silence")
        else:
            dialog2(get_next_say(replies, ""))
    #     next_phrase = silence(db)
    #     attempt += 1
    # elif len(text) == 0:  # not recognize
    #     dialog2(get_next_say(replies, ""))
    #     attempt += 1
    else:
        if not get_keyword():
            if is_repeat:
                return end_call("silence")
        # else:
        #     dialog2(get_next_say(replies, ""))
        else:
            toggle_keyword()
        dialog2(get_next_say(replies, text))
        
        
    # print('attempt', attempt) # for debug
    # if attempt == REPEAT:
    #     play_audio(next_phrase)
    #     return later(db)
    # if not end_call:
    #     next_phrase = dialog(next_phrase)
    # else:
    #     print('end_phrase', next_phrase)
    print("END OF DIALOG")
    return 0
'''





def dialog(say_obj, is_repeat=False, answer_time=5):
    """
    The function is the main logic for selecting the next phrase, recording speech, recognizing it.
    Return phrase for next step
    """

    global keyword, attempt, replies
    replies = say_obj.reply
    keyword = False
    next_is_repeat = False

    # if not is_repeat:
    play_audio(say_obj.say[0].audio)  # play speak_phrase from parameters
    if say_obj.cmd is not None:
        if not do_command(say_obj.cmd):
            return 0

    if replies is None: # <==================================== IN THIS NOT CORRECT IF REPEATED
        return 0

    # Waiting for an answer
    print('time to answer')
    for _ in range(10 * answer_time):
        if get_keyword():
            break
        time.sleep(0.1)

    text = get_phrases_from_speech(all_speeches[stage])
    print('text in dialog:', text)  # for debug
    if text is None or len(text) == 0:  # silence
        text = ''
        next_is_repeat = True
    else:
        if get_keyword():
            toggle_keyword()
            is_repeat = False
        else:
            next_is_repeat = True
            text = ''

    print('NEXT ANSWER')
    if not is_repeat:
        dialog(get_next_say(replies, text), is_repeat=next_is_repeat)
    print("END OF DIALOG")
    return 0





if __name__ == "__main__":
    with mic as source:
        r.adjust_for_ambient_noise(source)
    print('voice recording started')

    start_record = datetime.now()
    stop_listening = r.listen_in_background(source, callback, 5)

    # play_audio(dialog(db[0].answers[0].say, 4))
    dialog(root_say_obj)
    stop_listening()
    print('voice recording stopped')
    end_record = datetime.now()
    print(all_speeches)
    format_json(start_record, end_record, all_speeches)
