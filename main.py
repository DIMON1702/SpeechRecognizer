import speech_recognition as sr
import time
from business_logic import get_answer


def recognize_from_audiofile(recognizer, filename):
    """
    Function recognizes speech from the audiofile.
    Function returns text (str) or None if an error occurs.
    """

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    audiofile = sr.AudioFile(filename)

    with audiofile as source:
        audio = recognizer.record(source)
    try:
        result = r.recognize_google(audio)
    except sr.RequestError:
        print("Error! API unavailable")
    except sr.UnknownValueError:
        print("Error! Unable to recognize speech")
    else:
        return result


def speech_to_flac(recognizer, microphone, filename):
    """
    Function catches the speech using computer's microphone.
    And save it in the .flac file.
    """

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        print('Wait a second to adjust the ambient noise')
        recognizer.adjust_for_ambient_noise(source)
        print('Start your speech, please')
        audio = recognizer.listen(source)
        res = audio.get_flac_data()
        with open(filename, 'wb') as f:
            f.write(res)
        print("File created")
    return 0


def callback(recognizer, audio):
    try:
        speech = recognizer.recognize_google(audio)
        # print(speech)
    except sr.RequestError:
        print("Error! API unavailable")
    except sr.UnknownValueError:
        print("Error! Unable to recognize speech")
    except Exception as e:
        print(e)
    else:
        print(get_answer(speech))


if __name__ == "__main__":
    r = sr.Recognizer()  # Creating Recognizer object
    mic = sr.Microphone()  # Creating Microphone object
    # filename = "test.flac"
    # speech_to_flac(r, mic, filename)  # Saving speech to filename
    # text_from_audio = recognize_from_audiofile(r, filename)
    # print(text_from_audio)
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print('start speech')
    stop_listening = r.listen_in_background(source, callback)
    for _ in range(300):
        time.sleep(0.1)
