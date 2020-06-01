import asyncio
import websockets
import threading
import uuid
import datetime
from six.moves import queue
from google.cloud import speech
from google.cloud.speech import types
from google.cloud.speech import enums
import os

from settings import LANGUAGE


IP = 'localhost'
PORT = 2700
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/freeswitch/google_asr_key.json"


class Transcoder(object):
    # Converts audio chunks to text
    def __init__(self, uuid, encoding, rate, language):
        self.buff = queue.Queue()
        self.encoding = encoding
        self.language = language
        self.rate = rate
        self.closed = False
        self.finished = False
        self.transcript = None
        self.uuid = uuid

    def start(self):
        # Start up streaming speech call
        threading.Thread(target=self.process).start()

    def response_loop(self, responses):
        # Pick up the results of Speech to text conversion
        for response in responses:
            if not response.results:
                continue
            for result in response.results:
                if not result.alternatives:
                    continue
                # alternatives = result.alternatives
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    print(f"{datetime.datetime.now()}  {self.uuid}: "
                          f"FINAL RESULT: {transcript}")
                else:
                    print(f"{datetime.datetime.now()}  {self.uuid}: "
                          f"partial: {transcript}")

                self.finished = result.is_final
                self.transcript = transcript

    def process(self):
        # Audio stream recognition and result parsing
        # You can add speech contexts for better recognition

        metadata = types.RecognitionMetadata(
            interaction_type=enums.RecognitionMetadata.InteractionType.PHONE_CALL,
            recording_device_type=enums.RecognitionMetadata.RecordingDeviceType.PHONE_LINE,
            recording_device_name="Mobile phohecall"
        )

        cap_speech_context = types.SpeechContext(phrases=["כן"])
        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=self.encoding,
            sample_rate_hertz=self.rate,
            language_code=self.language,
            speech_contexts=[cap_speech_context, ],
            model='command_and_search',  # change model
            metadata=metadata
        )
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False)
        audio_generator = self.stream_generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        try:
            self.response_loop(responses)
            print(
                f"{datetime.datetime.now()}  {self.uuid}: SpeechClient - thread stopped")
        except:
            if not self.closed:
                self.start()
            else:
                print(
                    f"{datetime.datetime.now()}  {self.uuid}: SpeechClient - thread stopped")

    def stream_generator(self):
        while not self.closed:
            try:
                chunk = self.buff.get(timeout=2)
            except queue.Empty:
                continue
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self.buff.get(block=False, timeout=2)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)
        yield

    def write(self, data):
        # Writes data to the buffer
        self.buff.put(data)


async def audio_processor(websocket, path):
    # Collects audio from the stream, writes it to buffer and return the output of Google speech to text
    connection_id = uuid.uuid4()
    print(f"{datetime.datetime.now()}  {connection_id}: --->>> Open connection")
    print(f"{datetime.datetime.now()}  {connection_id}: Active threads: {threading.active_count()}")
    transcoder = Transcoder(
        uuid=connection_id,
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        rate=8000,
        language=LANGUAGE  # language='ru-RU'
    )

    transcoder.start()
    while True:
        try:
            data = await websocket.recv()
        except websockets.ConnectionClosed:
            print(
                f"{datetime.datetime.now()}  {transcoder.uuid}: <<<--- Connection closed @ recv")
            transcoder.closed = True
            break
        transcoder.write(data)
        transcoder.closed = False
        try:
            if transcoder.transcript:
                if transcoder.finished:
                    await websocket.send('{"text":"'+transcoder.transcript+'"}')
                else:
                    await websocket.send('{"partial":"'+transcoder.transcript+'"}')
                transcoder.transcript = None
        except:
            print(
                f"{datetime.datetime.now()}  {transcoder.uuid}: <<<--- Connection closed @ send")
            transcoder.closed = True
            break

start_server = websockets.serve(audio_processor, IP, PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
