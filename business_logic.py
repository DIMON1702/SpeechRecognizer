import pyttsx3


def get_answer(text):
    # logic to determine the answer
    answer = text
    text_to_speech(answer)
    return answer


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
