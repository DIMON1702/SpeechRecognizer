from pathlib import Path
import os.path
from pprint import pprint, pformat
from typing import List, Dict, Union, Iterator

from dataclasses import dataclass

import hashlib

# max allowed silence time in sec
MAX_SILENCE = 5
# max allowed response length in sec
MAX_RESPONSE = 17
VOICE_DIR = 'voice'

# types
Value = Union[str, int, float]


from gtts import gTTS
from pydub import AudioSegment

# path = 'audios/'

path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'audios', '')


def mp3_to_wav(filename):
    sound = AudioSegment.from_mp3(filename + '.mp3')
    sound.export(filename, format='wav')


# def wav_to_mp3(filename):
#     sound = AudioSegment.from_wav(filename + '.wav')
#     sound.export(filename + '.mp3', format='mp3')


def text_to_wav(text, filename, path=''):
    tts = gTTS(text)
    tts.save(path + filename + '.mp3')
    mp3_to_wav(path + filename)


@dataclass
class Node:
    text: str
    kids: List[str]


@dataclass
class Cmd:
    commands = (
        'goto', 
        'call_after_days',
        'remove_from_list',
        'call_after_min',
        'connect_salesperson'
    )
    cmd: str = None
    value: Value = None

    def __post_init__(self):
        assert self.cmd in self.commands, self.cmd


@dataclass
class Option:
    max_silence: float = MAX_SILENCE
    max_response: float = MAX_RESPONSE


@dataclass
class Hear:
    keyword: str
    # tag: str = None


@dataclass
class Voice:
    text: str
    audio: str = None  # file: 'voice/1.flac'


@dataclass
class Say:
    tag: str  # 1. intro
    hear: List[Hear] = None
    say: List[Voice] = None
    cmd: List[Cmd] = None
    option: Option = None
    reply: List['Say'] = None


def hash_text(text: str) -> str:
    hash = hashlib.md5()
    hash.update(bytes(text, 'utf8'))
    return hash.hexdigest()


def parse_dialog(text_lines: Iterator[str]) -> Dict[str, Say]:
    def build_nodes(lines: Iterator[str]) -> Dict[str, Node]:
        dic = {}
        for line in lines:
            if line and not line.startswith('#'):
                idx, _, txt = line.partition(' ')
                parent, _, _ = idx.rpartition('.')
                if not txt.lstrip().startswith('#'):
                    dic[idx] = Node(txt.strip(), [])
                    if parent:
                        dic[parent].kids.append(idx)
        return dic

    def get_option(kids: List[str]) -> Option:
        opt = {}
        for kid in kids:
            node = nodes[kid]
            option, _, value = node.text.strip().partition('=')
            opt[option] = value
        return Option(**opt)

    def get_cmd(kids: List[str]) -> List[Cmd]:
        commands = []
        for kid in kids:
            node = nodes[kid]
            cmd, _, value = node.text.strip().partition('=')
            commands.append(Cmd(cmd, value))
        return commands

    def get_say(node_id: str) -> Say:
        node = nodes[node_id]
        say = Say(node.text)
        for nid in node.kids:
            node = nodes[nid]
            verb = node.text.lower()
            assert node.text == verb.capitalize(), node
            if verb == 'say':
                say.say = [Voice(nodes[kid].text, path + hash_text(nodes[kid].text) + '.wav') for kid in node.kids]
                for voice in say.say:
                    # print(path + voice.audio, os.path.exists(path + voice.audio))
                    if not os.path.exists(voice.audio):
                        text_to_wav(voice.text, voice.audio)
            elif verb == 'hear':
                say.hear = [Hear(nodes[kid].text) for kid in node.kids]
            elif verb == 'option':
                say.option = get_option(node.kids)
            elif verb == 'reply':
                say.reply = [get_say(kid) for kid in node.kids]
            elif verb == 'cmd':
                say.cmd = get_cmd(node.kids)
            elif verb == 'goto':
                say.cmd = (say.cmd or []) + [Cmd('goto', nodes[node.kids[0]].text)]
        if say.tag and say.tag[0].isdigit():
            i = say.tag.split()[0].rstrip('.')
            dialog_dict[i] = say
        return say

    nodes = build_nodes(text_lines)
    Path(__file__).with_name('tmp_tree.txt').write_text(pformat(nodes))

    dialog_dict = {}
    root = get_say(nodes['1'].kids[0])
    dialog_dict['root'] = root
    return dialog_dict


if __name__ == '__main__':
    dialog = parse_dialog(Path('outgoing3.txt').read_text().splitlines())
    pprint(dialog)
