from gtts import gTTS
from pydub import AudioSegment

path = 'audios/'


def mp3_to_wav(filename):
    sound = AudioSegment.from_mp3(filename + '.mp3')
    sound.export(filename + '.wav', format='wav')


def wav_to_mp3(filename):
    sound = AudioSegment.from_wav(filename + '.wav')
    sound.export(filename + '.mp3', format='mp3')


def text_to_mp3(text, filename, path='audios/'):
    tts = gTTS(text)
    tts.save(path + filename + '.mp3')
    mp3_to_wav(path + filename)


if __name__ == "__main__":
    filename = 'intro'
    text = "Hi, this is Julia calling from Toyota. We have a sale going right now. Would you like to hear how you can save money on your car purchase today?"
    text_to_mp3(text, filename)
