import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
import soundfile as sf
import pyaudio
import wave

class SpeechDetector:
    def __init__(self, filename="temp.mp3", sample_rate=16000, window_size=1024, dynamic_threshold=True):
        self.filename = filename
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.dynamic_threshold = dynamic_threshold
        self.speech_intervals = []
        self.audio_data = None

    def record_audio(self, duration=5):
        print("Recording audio...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.window_size)
        frames = []

        for _ in range(0, int(self.sample_rate / self.window_size * duration)):
            data = stream.read(self.window_size)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open('temp.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.load_audio('temp.wav')
        print("Recording complete.")

    def load_audio(self, filename=None):
        if filename is None:
            filename = self.filename
        self.audio_data, self.sample_rate = sf.read(filename)
        if len(self.audio_data.shape) > 1:
            self.audio_data = self.audio_data.mean(axis=1)  # Convert to mono if stereo

    def compute_threshold(self, buffer_size=50):
        buffer = []
        threshold = 0
        for i in range(0, len(self.audio_data), self.window_size):
            frame = self.audio_data[i:i + self.window_size]
            frame_energy = np.sum(frame ** 2)
            buffer.append(frame_energy)
            if len(buffer) > buffer_size:
                buffer.pop(0)
            if self.dynamic_threshold:
                threshold = np.mean(buffer) + 2 * np.std(buffer)
            else:
                threshold = np.percentile(buffer, 75)
        return threshold

    def detect_speech(self):
        threshold = self.compute_threshold()
        print(f"Computed threshold: {threshold}")
        start_idx = None
        for i in range(0, len(self.audio_data), self.window_size):
            frame = self.audio_data[i:i + self.window_size]
            frame_energy = np.sum(frame ** 2)
            if frame_energy > threshold and start_idx is None:
                start_idx = i
            elif frame_energy <= threshold and start_idx is not None:
                end_idx = i
                self.speech_intervals.append((start_idx / self.sample_rate, end_idx / self.sample_rate))
                start_idx = None
        if start_idx is not None:
            self.speech_intervals.append((start_idx / self.sample_rate, len(self.audio_data) / self.sample_rate))

    def plot_intervals(self):
        times = np.arange(len(self.audio_data)) / self.sample_rate
        plt.figure(figsize=(10, 6))
        plt.plot(times, self.audio_data, label="Audio Signal")
        for start, end in self.speech_intervals:
            plt.axvspan(start, end, color='red', alpha=0.3, label="Speech Interval")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("Speech Detection Intervals")
        plt.legend()
        plt.show()

    def run(self, from_microphone=False, duration=5):
        if from_microphone:
            self.record_audio(duration)
        else:
            self.load_audio()
        self.detect_speech()
        self.plot_intervals()

if __name__ == "__main__":
    detector = SpeechDetector()
    detector.run()  # Set to False to use the temp.mp3 file
