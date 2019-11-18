from datetime import datetime, timedelta
import time
import json
import speech_recognition as sr
import soundfile as sf


results = []
folder = 'audios/'


def get_pauses(results):
    pauses = []
    if len(results) > 1:
        for index, res in enumerate(results[:-1]):
            pause = results[index + 1]["start_speech"] - res["end_speech"]
            pauses.append(pause.total_seconds())
    return pauses


def recognize_from_audio(r, audio):
    try:
        text = r.recognize_google(audio, language="en-US")
    except sr.RequestError:
        print("Error! API unavailable")
    except sr.UnknownValueError:
        print("Error! Unable to recognize speech")
        return None
    except Exception as e:
        print(e)
    else:
        return text


def start_listen(results, sec):
    """
    function listening in background and save all speeches\n
    sec - time in seconds to listening
    """
    start_record = datetime.now()
    for _ in range(10 * sec):
        time.sleep(0.1)
    end_record = datetime.now()

    start_pause = 0
    pauses = []
    if results:
        start_pause = (results[0]["start_speech"] - start_record).total_seconds()
        pauses = get_pauses(results)

    result_dict = {
        'start_record': start_record,
        'end_record': end_record,
        'audios': results,
        'start_pause': start_pause,
        'pauses': pauses
    }
    return result_dict


# if __name__ == "__main__":
#     start_listen(sr.Recognizer(), sr.Microphone(), 5)
