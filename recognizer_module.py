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
            pause = results[index + 1]["start_time"] - res["end_time"]
            pauses.append(pause.total_seconds())
    return pauses


def save_result_to_json(result_to_json):
    json_audios = result_to_json['audios']

    for res in json_audios:
        res['start_time'] = res['start_time'].strftime('%H_%M_%S')
        res['end_time'] = res['end_time'].strftime('%H_%M_%S')
        res.pop('audio')

    result_to_json['audios'] = json_audios
    result_to_json['start_record'] = result_to_json['start_record'].strftime(
        '%H_%M_%S')
    result_to_json['end_record'] = result_to_json['end_record'].strftime(
        '%H_%M_%S')

    json_filename = "data_{}.json".format(result_to_json['start_record'])
    with open(json_filename, 'w') as f:
        f.write(json.dumps(result_to_json))


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


# def callback(recognizer, audio):
#     end_time = datetime.now()
#     filename = "audio_{}.flac".format(end_time.strftime('%H_%M_%S'))
#     flac_data = audio.get_flac_data()
#     with open(folder + filename, 'wb') as f:
#         f.write(flac_data)

#     f = sf.SoundFile(folder + filename)
#     duration = len(f) / f.samplerate
#     start_time = end_time - timedelta(seconds=duration)

#     text = recognize_from_audio(recognizer, audio)
#     print(text)

#     result = {
#         'audio': audio,
#         'start_time': start_time,
#         'end_time': end_time,
#         'duration': duration,
#         'audio_filename': filename,
#         'text': text,
#     }
#     all_speaches[get_stage()].append(result)


def start_listen(results, sec):
    """
    function listening in background and save all speeches\n
    sec - time in seconds to listening
    """
    # global results
    # results = []
    # with mic as source:
    #     r.adjust_for_ambient_noise(source)
    #     print('start speech')

    start_record = datetime.now()
    # stop_listening = r.listen_in_background(source, callback)
    for _ in range(10 * sec):
        time.sleep(0.1)
    # stop_listening()
    end_record = datetime.now()

    start_pause = 0
    pauses = []
    if results:
        print(results[0])
        start_pause = (results[0]["start_time"] - start_record).total_seconds()
        pauses = get_pauses(results)

    result_dict = {
        'start_record': start_record,
        'end_record': end_record,
        'audios': results,
        'start_pause': start_pause,
        'pauses': pauses
    }
    copy_dict = result_dict.copy()
    # if copy_dict is result_dict:
    save_result_to_json(copy_dict)
    return result_dict


# if __name__ == "__main__":
#     start_listen(sr.Recognizer(), sr.Microphone(), 5)
