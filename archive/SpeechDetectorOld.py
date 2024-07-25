# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
import soundfile as sf
import pyaudio
import wave

class SpeechDetector:
    def __init__(self, filename="temp.mp3", sample_rate=16000, window_size=1024, dynamic_threshold=True, from_mic = True):
        self.filename = filename
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.dynamic_threshold = dynamic_threshold
        self.speech_intervals = []
        self.audio_data = None
        self.from_mic = from_mic

    def record_audio(self, duration=5):
        """
            Records audio of given duration. By default 5s

            Args:  
                duration (int): Duration of audio sample to be transcribed/speech detected
        """
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
        """
            A method for testing purposes. Load audio file to test speech detection
            Optional:
                filename (str): Optional audiofile name to be speech tested
        """
        if filename is None:
            filename = self.filename
        self.audio_data, self.sample_rate = sf.read(filename)
        if len(self.audio_data.shape) > 1:
            self.audio_data = self.audio_data.mean(axis=1)  # Convert to mono if stereo

    def compute_threshold(self, buffer_size=10):
        """
            A function that calculates the median threshold along the audio file
            Args:
                buffer_size (int): A frame ~sampling~ rate(i.e. threshold out of buffer_size) 
        """
        frame_energies = []

        # Collect frame energies
        for i in range(0, len(self.audio_data), self.window_size):
            frame = self.audio_data[i:i + self.window_size]
            frame_energy = np.sum(frame ** 2)
            frame_energies.append(frame_energy)

        # Calculate the dynamic threshold
        buffer = []
        thresholds = []

        for energy in frame_energies:
            buffer.append(energy)
            if len(buffer) > buffer_size:
                buffer.pop(0)
            if self.dynamic_threshold:
                threshold = np.mean(buffer) #+ 0.7 * np.std(buffer)
            else:
                threshold = np.percentile(buffer, 65)
            thresholds.append(threshold)

        # Use the median of all computed thresholds as the final threshold
        final_threshold = np.median(thresholds)
        return final_threshold

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
        self.speech_intervals = self.merge_intervals(self.speech_intervals)
        self.speech_intervals = self.filter_intervals(self.speech_intervals)
        return self.speech_intervals

    def merge_intervals(speech_intervals):
        """
            Static function that accepts speech intervals and merges continuos speech chunks, if the delay is less than 0.7s
            Args:
                speech_intervals (list(tuple(float, float))): A list of speech intervals
            Returns:
                list(tuple(float, float)): A list of merged speech chunks
        """
        merged_intervals = []
        for start, end in speech_intervals:
            if not merged_intervals or start - merged_intervals[-1][1] > 0.7:
                merged_intervals.append((start, end))
            else:
                merged_intervals[-1] = (merged_intervals[-1][0], end)
        return merged_intervals

    def filter_intervals(speech_intervals):
        """
            Static function that accepts speech intervals and deletes irregularities, if the chunk is no more than 0.2s
            Args:
                speech_intervals (list(tuple(float, float))): A list of speech intervals
            Returns:
                list(tuple(float, float)): A list of filtered speech intervals
        """
        return [(start, end) for start, end in speech_intervals if end - start > 0.2]

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

    def run(self, from_microphone=True, duration=5):
        if from_microphone:
            self.record_audio(duration)
        else:
            self.load_audio()
        # self.plot_intervals()
        print(self.speech_intervals)
        return self.detect_speech()

if __name__ == "__main__":
    detector = SpeechDetector()
    detector.run()  # Set to False to use the temp.mp3 file
