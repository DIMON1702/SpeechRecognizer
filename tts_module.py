import pyttsx3
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


def play_audio(filename):
    device = miniaudio.PlaybackDevice()
    f = sf.SoundFile(filename)
    duration = len(f) / f.samplerate
    stream = miniaudio.stream_file(filename)

    device.start(stream)
    time.sleep(duration)
    # input("Audio file playing in the background. Enter to stop playback: ")
    device.close()
