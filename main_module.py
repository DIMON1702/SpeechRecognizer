import speech_recognition as sr

from recognizer_module import start_listen
from tts_module import text_to_speech_espeak as tts_espeak
from tts_module import text_to_speech_rhvoice as tts_rhvoice

from pathlib import Path
import yaml
from answers import parse_answers, Step, Answer


tts = tts_espeak

def get_words_from_speach(speach):
    if len(speach['audios']) == 0: # silence
        return None

    res = [audio['text'].split(' ') for audio in speach['audios'] if audio['text'] is not None]
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


def accept(db, stage):
    print('accepted')
    tts(db[stage].answers[-1].say)
    dialog(stage + 1)
    return 0


def incorrect(db):
    print('incorrect')
    tts(db['incorrect'].answers[0].say)
    return 4


def end_call(text):
    print('exit')
    tts(text)
    return 0


def next_choise(command, db, stage):
    if command == 'REJECT':
        result = rejection(db)
    elif command == 'LATER':
        result = later(db)
    elif command == 'ACCEPT':
        result = accept(db, stage)
    elif command == 'EXIT':
        result = end_call(db[stage].answers[-1].say)
    else:
        result = 'error'
    return result


def get_answer(text, db, stage):
    """
    text - list of words from user response
    db - dict with answers from yaml file
    stage - start position in file  
    """
    for answer in db[stage].answers:
        for word in text:
            if word in answer.keyword:
                answer = next_choise(answer.cmd, db, stage)
                return answer
    return incorrect(db)


def dialog(stage):
    for _ in range (2): # repeats
        text = get_words_from_speach(start_listen(r, mic, 5))
        if text is None: # silence
            silence(db)
        elif len(text) == 0: # not recognize
            incorrect(db)
        else:
            answer = get_answer(text, db, stage)
            if answer == 4:
                continue
            break

r = sr.Recognizer()  # Creating Recognizer object
mic = sr.Microphone()  # Creating Microphone object

data = yaml.safe_load(Path('answers.yaml').open())
db = parse_answers(data)

if __name__ == "__main__":
    tts(db[0].answers[0].say) # first phrase
    dialog(1)
