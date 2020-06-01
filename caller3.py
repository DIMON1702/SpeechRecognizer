# TODO: добавить распараллеливание звонков и счетчик активных вызовов
# TODO: Выполнять параллельно несколько звонков, не больше n в один момент времени

import ESL
import sys
import os
from pathlib import Path
import logging
import pickle

from settings import SESSIONS_FILE_PATH, CALLER_NUMBER

import say

# from sms import send_sms

logger = logging.getLogger('CallLogger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs_call.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.info("====PROGRAM WAS STARTED=====")

if len(sys.argv) != 3:
    logger.error("Invalid parametrs")
    raise AttributeError(
        f"Invalid number of parameters ({len(sys.argv) - 1}). "
        f"Must be 2 (file name with phrases and file with numbers)"
    )
text_file = sys.argv[1]
phone_numbers_file = sys.argv[2]
logger.info(
    f'Answers tree file "{text_file}", '
    f'phone numbers file {phone_numbers_file}')


# parse answer's tree
db = say.parse_dialog(Path(text_file).read_text().splitlines())
logger.debug('Answer tree read successfully')
root_say_obj = db.get("root")
repeat_phrases = db.get("repeat").say
replies = root_say_obj.reply
data = {
    "root": root_say_obj,
    "repeat": repeat_phrases,
    "repeat_counter": 0
}


def put_pickle_data_to_file(filepath, data):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def create_local_call(parallel_mode=False):
    logger.info('Test call')
    bg = 'bgapi ' if parallel_mode else ''
    os.system(
        f'{FS_CLI}"{bg}lua make_call.lua sofia/external/1002@45.145.0.53"')


def create_external_call(number, caller_number=CALLER_NUMBER,
                         parallel_mode=False):

    logger.info('Calling to {}'.format(number))
    bg = 'bgapi ' if parallel_mode else ''

    os.system(f'{FS_CLI}"{bg}lua make_call.lua '
              f'{{origination_caller_id_number={caller_number}}}'
              f'sofia/external/38490#{number}@176.9.119.112"')


def call_numbers(number_list, parallel_mode=False):
    for call_number in number_list:
        if call_number == 'test':
            create_local_call(parallel_mode)
        else:
            create_external_call(call_number, parallel_mode=parallel_mode)


if __name__ == "__main__":
    put_pickle_data_to_file(SESSIONS_FILE_PATH + 'default.pickle', data)
    FS_CLI = "fs_cli -x "
    with open(phone_numbers_file, 'r') as f:
        call_list = f.read().splitlines()
    call_numbers(call_list, parallel_mode=False)
