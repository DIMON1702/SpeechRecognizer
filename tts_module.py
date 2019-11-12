import pyttsx3
import sys
sys.path.append('/usr/lib/python3/dist-packages/')
import speechd


def text_to_speech_espeak(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-50)
    engine.setProperty('voice', 'english+1')
    engine.say(text)
    engine.runAndWait()


def text_to_speech_rhvoice(text):
    tts_d = speechd.SSIPClient('test')
    tts_d.set_output_module('rhvoice')
    tts_d.set_rate(10) # Read speed (-100, 100)
    # tts_d.set_language('en')
    # tts_d.set_voice('male2')
    tts_d.set_synthesis_voice('Elena+CLB')
    # tts_d.set_pitch(0) # Voice pitch (-100, 100)
    tts_d.set_punctuation(speechd.PunctuationMode.SOME)
    tts_d.speak(text)
    # print(tts_d.list_synthesis_voices())
    tts_d.close()

# if __name__ == "__main__":
#     text_to_speech_rhvoice('Hi, this is John calling from Toyota. We have a sale going right now. Would you like to hear how you can save money on your car purchase today?')