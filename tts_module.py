import pyttsx3
from gtts import gTTS
import pyaudio
import miniaudio
import time
import soundfile as sf

import sys
sys.path.append('/usr/lib/python3/dist-packages/')
import speechd


engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)
engine.setProperty('voice', 'english+1')


def text_to_speech_espeak(text):
    engine.say(text)
    engine.runAndWait()
    print('----------runAndWait-----------')


from gtts import gTTS

path = 'audios/'
filename = '*.mp3'
text = ''


def text_to_mp3(text, filename, path='audios/'):
    tts = gTTS(text)
    tts.save(path + filename)


def text_to_speech_rhvoice(text):
    tts_d = speechd.SSIPClient('test')
    tts_d.set_output_module('rhvoice')
    # tts_d.set_rate(-10) # Read speed (-100, 100)
    # tts_d.set_language('en')
    # tts_d.set_voice('male2')
    # tts_d.set_synthesis_voice('Alan')
    # tts_d.set_pitch(0) # Voice pitch (-100, 100)
    # tts_d.set_punctuation(speechd.PunctuationMode.SOME)
    tts_d.speak(text)
    # print(tts_d.list_synthesis_voices())
    tts_d.close()


device = miniaudio.PlaybackDevice()


def get_stop():
    from _main import keyword
    return keyword

def play_audio(filename):
    print(filename)
    f = sf.SoundFile(filename)
    duration = len(f) / f.samplerate
    stream = miniaudio.stream_file(filename)
    print(duration)
    device.start(stream)
    for _ in range (10 * (int(duration) + 1)):
        if get_stop():
            break
        time.sleep(0.1)
    # input("Audio file playing in the background. Enter to stop playback: ")
    try:
        device.stop()
    except Exception as e:
        print(e)
