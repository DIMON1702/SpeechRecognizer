from freeswitchESL import ESL
import os, sys
from datetime import datetime
from pathlib import Path
import time

import speech_recognition as sr
from recognizer_module import recognize_from_audio

EXIT = False
HANGUP_COMMANDS = [2, 3, 4, 5]

if len(sys.argv) != 3:
    raise AttributeError("Invalid number of parameters ({}). Must be 2 (language and file name with phrases)".format(
        len(sys.argv)-1))
language = sys.argv[1]
text_file = sys.argv[2]
number = 'local' # '972527955710'

record_files_path = '/var/lib/freeswitch/recordings/' # /opt/freeswitch/recordings/
local_record_files_path = '/opt/freeswitch/recordings/'
phrase_files_path = '/var/lib/freeswitch/recordings/' # '/opt/freeswitch/play/'
# phrase_files_path = '/opt/freeswitch/recordings/'
current = 1
# language = "en-US"


import say
db = say.parse_dialog(Path(text_file).read_text().splitlines())
root_say_obj = db.get("root")
replies = root_say_obj.reply

stage = 0
all_speeches = [[]]
keyword = False
attempt = 0
uuid = ''

def create_local_call():
    os.system(FS_CLI + '"originate sofia/external/1002@45.145.0.53 9090"')
    

def create_external_call(number, caller_number='972035057669'):
    os.system(FS_CLI + '"originate {origination_caller_id_number=' + caller_number + '}sofia/external/38490#' + number + '@176.9.119.112 9090"')
    # os.system(FS_CLI + '"originate sofia/external/38490#972527955710@176.9.119.112 9090"') # Michael


def record_answer(uuid, filename, time=5):
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
    """
    if not replies:
        return 0
    # if only_check:
    #     print('REPLIES', replies)
    keywords = {replies.index(
        say_o): [keyword.keyword for keyword in say_o.hear] for say_o in replies}
    for key, value in keywords.items():
        for val in value:
            if val in speech:
                if only_check:
                    return True
                return replies[key]
    if only_check:
        return False
    return replies[-1]


def get_phrases_from_speech(speech_stage):
    """
    Function returns list of phrases from current stage
    """
    if len(speech_stage) == 0:  # silence
        return None
    print('STAGE\n', speech_stage)
    res = [speech for speech in speech_stage if speech is not None]
    print(res)  # for debug
    return res


def do_command(commands):
    global replies
    for command in commands:
        if command.cmd == 'goto':
            replies = db.get(command.value).reply
            return 1
        elif command.cmd == 'call_after_days':
            print(command.cmd, command.value)
            return 2
        elif command.cmd == 'remove_from_list':
            print(command.cmd, command.value)
            return 3
        elif command.cmd == 'call_after_min':
            print(command.cmd, command.value)
            return 4
        elif command.cmd == 'connect_salesperson':
            print(command.cmd, command.value)
            return 5
        else:
            print('Incorrect command')
            return 0


def event_handler(con, say_obj, is_repeat=False, next_is_repeat=False, hangup=False):
    global current, uuid, number
    global stage

    if hangup:
        return EXIT
    replies = say_obj.reply

    e = con.recvEvent()
    uuid = e.getHeader('Unique-ID')
    ename = e.getHeader('Event-name')
    if ename == 'CHANNEL_ANSWER':
        number = e.getHeader('Caller-Destination-Number')

        # TODO: change 1th phrase
        # phrase_file = record_files_path + 'intro1.wav' # first phrase
        # play_file(uuid, phrase_file)

        next_play = phrase_files_path + say_obj.say[0].audio # next_phrase
        print('next_phrase_file=', next_play)
        play_file(uuid, next_play)
        

    elif ename == 'PLAYBACK_STOP':
        # after stop playback need start recording speech
        curr_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        playback_file = e.getHeader('Playback-File-Path')
        next_play = record_files_path + '{}_{}_{}.wav'.format(number, curr_datetime, str(current))
        print('Recording start')
        record_answer(uuid, next_play)
    elif ename == 'RECORD_STOP':
        # After stop record need recognize speech and choose the next phrase for playing
        record_file = e.getHeader('Record-File-Path').split('/')[-1]
        audioinput = sr.AudioFile(local_record_files_path + record_file)
        with audioinput as source:
            audio = r.record(source)
            text = recognize_from_audio(r, audio, language)
            all_speeches[stage].append(text) # add text to current stage
            print('all_speeches\n', all_speeches)

        # main_logiс
        if text:
            say_obj = get_next_say(replies, text)
        print(say_obj)
        if say_obj.cmd is not None:
            command_res = do_command(say_obj.cmd)
            if command_res:
                next_play = phrase_files_path + say_obj.say[0].audio # next_phrase
                print('next_phrase_file=', next_play)
                play_file(uuid, next_play)
                return {'say_obj': get_next_say(replies, text), 'is_repeat':next_is_repeat, 'hangup': command_res in HANGUP_COMMANDS}
            else:
                return EXIT

        if replies is None:
            return EXIT

        text = get_phrases_from_speech(all_speeches[stage])
        print('text in dialog:', text)  # for debug
        keyword = get_next_say(replies, text, only_check=True)

        if text is None or len(text) == 0:  # silence
            text = ''
            next_is_repeat = True
        else:
            if keyword:
                is_repeat = False
            else: # not understand
                next_is_repeat = True
                text = ''

        # TODO: Must be global

        if not is_repeat:
            all_speeches.append([])
            stage += 1
            # next_play
            next_play = phrase_files_path + say_obj.say[0].audio # next_phrase
            print('next_phrase_file=', next_play)
            play_file(uuid, next_play)
            return {'say_obj': get_next_say(replies, text), 'is_repeat':next_is_repeat}# dialog2(get_next_say(replies, text), is_repeat=next_is_repeat)
        else:
            print('FOREVER SILENCE')  # must be voice

    elif ename == 'CHANNEL_HANGUP':
        hangup(uuid)
        return EXIT
    else:
        print('ename=', ename)
    return {'say_obj': say_obj}


if __name__ == "__main__":
    FS_CLI = "docker exec -i -t freeswitch /usr/bin/fs_cli -x" #это путь к fs_cli, она в докере так что через докер экзек
    con = ESL.ESLconnection('localhost', '8021', 'ClueCon')
    con.events('json', 'CHANNEL_ANSWER PLAYBACK_STOP RECORD_STOP CHANNEL_HANGUP')
    res = {'say_obj': root_say_obj} #

    r = sr.Recognizer()

    if con.connected():
        # create_external_call('972527955710')
        create_local_call()
        while res:
            res = event_handler(con, **res)
            # print('res=', res)
        time.sleep(3)
        print('Hangup')
        hangup(uuid)
    else:
        print('Not connected!')
