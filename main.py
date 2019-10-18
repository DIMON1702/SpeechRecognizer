import speech_recognition as sr


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


if __name__ == "__main__":
    r = sr.Recognizer()  # Creating Recognizer object
    mic = sr.Microphone()  # Creating Microphone object
    filename = "test.flac"
    speech_to_flac(r, mic, filename)  # Saving speech to filename
    text_from_audio = recognize_from_audiofile(r, filename)
    print(text_from_audio)
