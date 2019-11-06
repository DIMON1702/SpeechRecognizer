import speech_recognition as sr
import time
from datetime import datetime, timedelta
import json
from business_logic import get_answer

import soundfile as sf

results = []
folder = 'audios/'


def get_pauses(results):
    pauses = []
    if len(results) > 1:
        for index, res in enumerate(results[:-1]):
            pause = results[index + 1]["start_time"] - res["end_time"]
            pauses.append(pause.total_seconds())
    return pauses


def save_result_to_json(result_dict):
    json_audios = result_dict['audios']

    for res in json_audios:
        res['start_time'] = res['start_time'].strftime('%H:%M:%S')
        res['end_time'] = res['end_time'].strftime('%H:%M:%S')
        res.pop('audio')

    result_dict['audios'] = json_audios
    result_dict['start_record'] = result_dict['start_record'].strftime(
        '%H:%M:%S')
    result_dict['end_record'] = result_dict['end_record'].strftime('%H:%M:%S')

    json_filename = "data_{}.json".format(result_dict['start_record'])
    with open(json_filename, 'w') as f:
        f.write(json.dumps(result_dict))


def recognize_from_audio(r, audio):
    try:
        text = r.recognize_google(audio)
        print(text)
    except sr.RequestError:
        print("Error! API unavailable")
    except sr.UnknownValueError:
        print("Error! Unable to recognize speech")
    except Exception as e:
        print(e)
    else:
        return text


def callback(recognizer, audio):
    end_time = datetime.now()
    filename = "audio_{}.flac".format(end_time.strftime('%H_%M_%S'))
    flac_data = audio.get_flac_data()
    with open(folder + filename, 'wb') as f:
        f.write(flac_data)

    f = sf.SoundFile(folder + filename)
    duration = len(f) / f.samplerate
    start_time = end_time - timedelta(seconds=duration)

    text = recognize_from_audio(recognizer, audio)

    result = {
        'audio': audio,
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'audio_filename': filename,
        'text': text,
    }
    results.append(result)


def start_listen(r, mic, sec):
    """
    function listening in background and save all speeches\n
    sec - time in seconds to listening
    """
    global results
    results = []
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print('start speech')

    start_record = datetime.now()
    stop_listening = r.listen_in_background(source, callback)
    for _ in range(10 * sec):
        time.sleep(0.1)

    end_record = datetime.now()

    if results:
        start_pause = (results[0]["start_time"] - start_record).total_seconds()
        pauses = get_pauses(results)

    result_dict = {
        'start_record': start_record,
        'end_record': end_record,
        'audios': results,
        'start_pause': start_pause,
        'pauses': pauses
    }

    save_result_to_json(result_dict.copy())
    return result_dict


if __name__ == "__main__":
    r = sr.Recognizer()  # Creating Recognizer object
    mic = sr.Microphone()  # Creating Microphone object
    data = start_listen(r, mic, 10)
    text = [audio['text'] for audio in data['audios']]
    get_answer('. '.join(text))
