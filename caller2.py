from freeswitchESL import ESL
import os, sys
from datetime import datetime
from pathlib import Path
import time

import speech_recognition as sr
from recognizer_module import recognize_from_audio

import say


if len(sys.argv) != 3:
    raise AttributeError("Invalid number of parameters ({}). Must be 2 (language and file name with phrases)".format(
        len(sys.argv)-1))
language = sys.argv[1]
text_file = sys.argv[2]
number = 'local' # '972527955710'

EXIT = False
# REPEAT = 1
DEFAULT_ANSWER_TIME = 5 # sec
record_files_path = '/var/lib/freeswitch/recordings/' # /opt/freeswitch/recordings/
local_record_files_path = '/opt/freeswitch/recordings/'
phrase_files_path = '/var/lib/freeswitch/recordings/' # TODO: Change file path in docker '/opt/freeswitch/play/'
CURRENT = 1

# parse answer's tree
db = say.parse_dialog(Path(text_file).read_text().splitlines())
root_say_obj = db.get("root")
replies = root_say_obj.reply


def create_local_call():
    os.system(FS_CLI + '"originate sofia/external/1002@45.145.0.53 9090"')
    

def create_external_call(number, caller_number='972035057669'):
    os.system(FS_CLI + '"originate {origination_caller_id_number=' + caller_number + '}sofia/external/38490#' + number + '@176.9.119.112 9090"')
    # os.system(FS_CLI + '"originate sofia/external/38490#972527955710@176.9.119.112 9090"') # Michael


def record_answer(uuid, filename, time=DEFAULT_ANSWER_TIME):
    # os.system(FS_CLI + '"uuid_record ' + uuid + ' start /var/lib/freeswitch/recordings/chemax_test_3.wav 5"')
    os.system('{}"uuid_record {} start {} {}"'.format(FS_CLI, uuid, filename, time)) # async


def play_file(uuid, filename):
    # os.system(FS_CLI + '"uuid_broadcast ' + uuid + ' /var/lib/freeswitch/recordings/chemax_test_1.wav both"')
    os.system('{}"uuid_broadcast {} {} both"'.format(FS_CLI, uuid, filename)) # async


def hangup(uuid):
    # os.system(FS_CLI + '"uuid_kill ' + uuid + '"')
    os.system('{}"uuid_kill {}"'.format(FS_CLI, uuid))


def get_next_say(replies, speech, only_check=False):
    """
    function seeks words and phrases in lists and returns the appropriate command
    or last if no words in keywords
    """
    # if not replies:
    #     return 0
    keywords = {replies.index(
        say_o): [keyword.keyword for keyword in say_o.hear] for say_o in replies}
    for key, value in keywords.items():
        for val in value:
            if val in speech:
                if only_check:
                    return True
                return replies[key]
    return False # reply False if not 


# def get_words_from_speech(phrase):
#     res = phrase.split() if phrase else None
#     print(res) # DEBUG
#     return res


HANGUP_COMMANDS = [5]


def do_command(command):
    global replies
    if command.cmd == 'goto':
        replies = db.get(command.value).reply
        return 1
    # elif ...
    elif command.cmd == 'connect_salesperson':
        print(command.cmd, command.value)
        return 5
    else:
        print('Incorrect command')
        return 0


def event_handler(con, say_obj, next_hangup=False, **kwargs):
    global uuid, number, CURRENT


    if next_hangup:
        hangup(uuid)

    REPEAT = {'say_obj': say_obj}

    replies = say_obj.reply
    if not replies:
        next_hangup = True
        print('NOT REPLIES!!!')
        # return {'say_obj': say_obj, 'next_hangup': True} # NO answers

    e = con.recvEvent()
    uuid = e.getHeader('Unique-ID')
    ename = e.getHeader('Event-name')
    print(ename)
    

    # answer a call
    if ename == 'CHANNEL_ANSWER':
        number = e.getHeader('Caller-Destination-Number') # for local numbers else 9090
        next_play = phrase_files_path + say_obj.say[0].audio # next_phrase
        print('next_play', next_play)
        time.sleep(1.5)
        play_file(uuid, next_play)
        return {'say_obj': say_obj, 'res': 1}

    elif ename == 'PLAYBACK_STOP':
        try:
            answer_time = say_obj.option.max_response
        except:
            answer_time = DEFAULT_ANSWER_TIME
        # after stop playback need start recording speech
        curr_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # playback_file = e.getHeader('Playback-File-Path')
        next_record = record_files_path + '{}_{}_{}.wav'.format(number, curr_datetime, str(CURRENT))
        print('Recording start')
        record_answer(uuid, next_record, answer_time)
        CURRENT += 1
        return {'say_obj': say_obj, 'res': 2}

    elif ename == 'RECORD_STOP':
        # After stop record need recognize speech and choose the next phrase for playing
        record_file = e.getHeader('Record-File-Path').split('/')[-1]
        audioinput = sr.AudioFile(local_record_files_path + record_file)
        with audioinput as source:
            audio = r.record(source)
            text = recognize_from_audio(r, audio, language)
            print('recognized text', text)
        
        if not text:
            play_file(uuid, phrase_files_path + say_obj.say[0].audio)
            return {'say_obj': say_obj, 'next_hangup': next_hangup}
        elif not get_next_say(replies, text, only_check=True): # if not recognize next reply
            play_file(uuid, phrase_files_path + say_obj.say[0].audio)
            return REPEAT
        else:
            new_say_obj = get_next_say(replies, text)
        
        next_play = phrase_files_path + new_say_obj.say[0].audio
        print('next_phrase_file=', next_play)
        play_file(uuid, next_play)

        if say_obj.cmd is not None:
            command_res = do_command(say_obj.cmd[0])
            if command_res in HANGUP_COMMANDS:
                next_hangup = True
        
        say_obj = new_say_obj
        print('!!!next_hangup=', next_hangup)
        return {'say_obj': say_obj, 'next_hangup': next_hangup}


if __name__ == "__main__":
    FS_CLI = "docker exec -i -t freeswitch /usr/bin/fs_cli -x" #это путь к fs_cli, она в докере так что через докер экзек
    con = ESL.ESLconnection('localhost', '8021', 'ClueCon')
    con.events('json', 'CHANNEL_ANSWER PLAYBACK_STOP RECORD_STOP CHANNEL_HANGUP')
    res = {'say_obj': root_say_obj}

    r = sr.Recognizer()

    if con.connected():
        # create_external_call('972527955710') # ('972545737175') # Юра
        create_local_call()
        while True:
            res = event_handler(con, **res)
            print('res=', res)
            if not res:
                break
        # time.sleep(3)
        print('Hangup main')
        hangup(uuid)
    else:
        print('Not connected!')
