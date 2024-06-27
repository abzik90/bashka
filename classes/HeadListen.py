import pyaudio
from pynput import keyboard
import wave
from pydub import AudioSegment
import threading

# Constants for the audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
TEMP_WAV_FILE = "temp.wav"

class HeadListen:
    def __init__(self, destination_filename):
        self.destination_filename = destination_filename
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.recording = False
        self.thread = None

    def on_press(self, key):
        if key == keyboard.Key.space and not self.recording:
            print("spacebar key was pressed")
            self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True,
                                      frames_per_buffer=CHUNK)
            self.recording = True
            self.frames = []
            self.thread = threading.Thread(target=self.record_audio)
            self.thread.start()

    def on_release(self, key):
        if key == keyboard.Key.space and self.recording:
            print("spacebar key was released")
            self.recording = False
            self.thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            with wave.open(TEMP_WAV_FILE, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(self.frames))

            self.convert_wav_to_mp3(TEMP_WAV_FILE, self.destination_filename)
            return False

    def record_audio(self):
        while self.recording:
            print("I'm recording!")
            data = self.stream.read(CHUNK)
            self.frames.append(data)

    def convert_wav_to_mp3(self, wav_file, mp3_file):
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format="mp3")
        print(f"File saved as {mp3_file}")

    def listener(self):
        # Collect events until released
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
