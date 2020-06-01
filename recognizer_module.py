import speech_recognition as sr


def recognize_from_audio(r, audio, language="en-US"):
    try:
        text = r.recognize_google(audio, language=language)
    except sr.RequestError:
        print("Error! API unavailable")
    except sr.UnknownValueError:
        # print("Error! Unable to recognize speech")
        return None
    except Exception as e:
        print(e)
    else:
        return text
