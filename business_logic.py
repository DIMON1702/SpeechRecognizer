import pyttsx3
import sys
sys.path.append('/usr/lib/python3/dist-packages/')
import speechd


def get_answer(text):
    # logic to determine the answer
    answer = text
    text_to_speech_rhvoice(answer)
    return answer


def text_to_speech_espeak(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-50)
    engine.setProperty('voice', 'english+f2')
    engine.say(text)
    engine.runAndWait()


def text_to_speech_rhvoice(text):
    tts_d = speechd.SSIPClient('test')
    tts_d.set_output_module('rhvoice')
    tts_d.set_rate(10) # Read speed (-100, 100)
    # tts_d.set_language('ru')
    # tts_d.set_voice('female2')
    tts_d.set_synthesis_voice('Clb')
    tts_d.set_pitch(-10) # Voice pitch (-100, 100)
    tts_d.set_punctuation(speechd.PunctuationMode.SOME)
    tts_d.speak(text)
    # print(tts_d.list_synthesis_voices())
    tts_d.close()
