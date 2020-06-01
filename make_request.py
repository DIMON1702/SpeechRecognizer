# TODO: Настроить логгер

from datetime import datetime
import sys
import os.path
from shutil import copy as sh_copy
import json
import pickle

import logging

import speech_recognition as sr
from recognizer_module import recognize_from_audio

from settings import MAIN_FILE_PATH, SESSIONS_FILE_PATH, PHRASES_FILE_PATH
from settings import CALLER_NUMBER_TO_SALES, SALES_NUMBER


logger = logging.getLogger('RequestLogger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(MAIN_FILE_PATH + 'logs_call.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_pickle_data_from_file(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data


def put_pickle_data_to_file(filepath, data):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def get_next_say(replies, speech, only_check=False):
    """
    Function seeks words and phrases in lists 
    and returns the appropriate command or last if no words in keywords
    """
    keywords = {replies.index(say_o): [
        keyword.keyword for keyword in say_o.hear] for say_o in replies}
    for key, value in keywords.items():
        for val in value:
            if val in speech:
                if only_check:
                    return True
                return replies[key]
    return False  # reply False if not


def do_command(command):
    if command.cmd == 'connect_salesperson':
        return {
            "action": "transfer",
            "data":
            f"{{origination_caller_id_number={CALLER_NUMBER_TO_SALES}}}"
            f"sofia/external/38490#{SALES_NUMBER}@176.9.119.112"
        }
    if command.cmd == 'hangup':
        return {"action": "disconnect"}
    # elif ...
    else:
        print('Incorrect command')
        return {}


def get_result(uuid, text, confirm):
    next_hangup = False
    result = []

    data_obj = get_pickle_data_from_file(SESSIONS_FILE_PATH +
                                         uuid + '.pickle')
    say_obj = data_obj.get('root')
    repeat = data_obj.get('repeat')
    repeat_counter = data_obj.get('repeat_counter')
    replies = say_obj.reply

    if text == "answer_timeout":
        if repeat_counter < 2:
            res = [{
                "action": "speak",
                "data": PHRASES_FILE_PATH + repeat[repeat_counter].audio
            }]
            logger.info(res)

            new_data_obj = {
                "root": say_obj,
                "repeat": repeat,
                "repeat_counter": repeat_counter + 1
            }
            put_pickle_data_to_file(
                SESSIONS_FILE_PATH + uuid + '.pickle', new_data_obj)
        else:
            res = [{"action": "disconnect"}]
        return json.dumps(res)

    if not text:
        logger.warning('No recognized text! Play repeat phrase "{}"'.format(
            repeat[repeat_counter].audio))
        return json.dumps([])
    elif not get_next_say(replies, text, only_check=True):
        # if not recognize next reply
        logger.warning('No recognized text in current branch! ' +
                       'Play repeat phrase "{}"'.format(repeat[repeat_counter].audio))
        return json.dumps([])
    else:
        new_say_obj = get_next_say(replies, text)

    try:
        next_play = PHRASES_FILE_PATH + new_say_obj.say[0].audio
        logger.info('Played message "{}"'.format(next_play))
        result = [{"action": "speak", "data": next_play}]
    except Exception as e:
        logger.error(e)
        new_say_obj = say_obj

    say_obj = new_say_obj

    if say_obj.cmd is not None:
        result.append(do_command(say_obj.cmd[0]))
    elif not new_say_obj.reply:
        next_hangup = True
        logger.info('The last phrase in the tree')

    new_data_obj = {
        "root": say_obj,
        "repeat": repeat,
        "repeat_counter": 0
    }
    if confirm == 'confirm':
        put_pickle_data_to_file(
            SESSIONS_FILE_PATH + uuid + '.pickle', new_data_obj)

    if next_hangup:
        result.append({"action": "disconnect"})

    logger.info(result)
    if next_hangup:
        logger.info("=======================================================")
    return json.dumps(result)


def first_answer(uuid):
    sh_copy(SESSIONS_FILE_PATH + 'default.pickle',
            SESSIONS_FILE_PATH + uuid + '.pickle')
    data = get_pickle_data_from_file(SESSIONS_FILE_PATH + 'default.pickle')
    first_phrase = data.get("root").say[0].audio
    res = [{"action": "speak", "data": PHRASES_FILE_PATH + first_phrase}]
    logger.info(res)
    return json.dumps(res)


if __name__ == "__main__":
    r = sr.Recognizer()
    uuid = sys.argv[1]
    text = sys.argv[2]
    confirm = sys.argv[3]
    logger.info('TEXT: ' + text)
    if os.path.exists(SESSIONS_FILE_PATH + uuid + '.pickle'):
        print(get_result(uuid, text, confirm))
    else:
        logger.info('=================Start call==============')
        logger.info('UUID: "{}"'.format(uuid))
        print(first_answer(uuid))
