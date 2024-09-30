# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
import soundfile as sf
import pyaudio
import wave
import threading

class SpeechDetector:
    def __init__(self, sample_rate=16000, window_size=1024, dynamic_threshold=True):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.dynamic_threshold = dynamic_threshold
        self.speech_intervals = []
        self.audio_data = None
        self.frames = []
        self.p = pyaudio.PyAudio()
    def __del__(self):
        self.p.terminate()
        
    def record_audio(self, duration=5):
        """
            Records audio of given duration. By default 5s

            Args:  
                duration (int): Duration of audio sample to be transcribed/speech detected
        """
        print("Recording audio...")
        stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.window_size)
        
        frames_current = []
        for _ in range(0, int(self.sample_rate / self.window_size * duration)):
            data = stream.read(self.window_size)
            self.frames.append(data)
            frames_current.append(data)

        stream.stop_stream()
        stream.close()
        # write current duration(5s) chunk to temporary listen_current.wav file
        self.write_wav(frames = frames_current, filename = "listen_current.wav")
        self.load_audio()
        print("Recording complete.")
    
    def write_wav(self, frames, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    def load_audio(self):
        """
            A method for testing purposes. Load audio file to test speech detection
            Optional:
                filename (str): Optional audiofile name to be speech tested
        """
        filename = "listen_current.wav"
        self.audio_data, self.sample_rate = sf.read(filename)
    
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

    def detect_speech(self, start = 0):
        threshold = self.compute_threshold()
        print(f"Computed threshold: {threshold}")
        # return if background noise
        if threshold < 1:
            return
        start_idx = None
        for i in range(0, len(self.audio_data), self.window_size):
            frame = self.audio_data[i:i + self.window_size]
            frame_energy = np.sum(frame ** 2)
            if frame_energy > threshold and start_idx is None:
                start_idx = i
            elif frame_energy <= threshold and start_idx is not None:
                end_idx = i
                self.speech_intervals.append((start + start_idx / self.sample_rate, start + end_idx / self.sample_rate))
                start_idx = None
        if start_idx is not None:
            self.speech_intervals.append((start + start_idx / self.sample_rate, start + len(self.audio_data) / self.sample_rate))
        # print("Pre-processed",self.speech_intervals)
        self.merge_intervals()
        self.filter_intervals()

    def merge_intervals(self):
        """
            Static function that accepts speech intervals and merges continuos speech chunks, if the delay is less than 0.7s
        """
        merged_intervals = []
        for start, end in self.speech_intervals:
            if not merged_intervals or start - merged_intervals[-1][1] > 0.7:
                merged_intervals.append((start, end))
            else:
                merged_intervals[-1] = (merged_intervals[-1][0], end)
        self.speech_intervals = merged_intervals

    def filter_intervals(self):
        """
            Static function that accepts speech intervals and deletes irregularities, if the chunk is no more than 0.2s
        """
        self.speech_intervals = [(start, end) for start, end in self.speech_intervals if end - start > 0.2]


    def run(self, head, duration=5):
        print(id(head))

        while True:
            self.frames = []
            self.speech_intervals = []  
            self.audio_data = None
            run_num = 0

            # if list isn't empty and isn't in range 4.3 < end <= 5
            while True:
                recording_thread = threading.Thread(target=self.record_audio, args = (duration,))
                self.detect_speech(run_num*duration)
                recording_thread.start()
                recording_thread.join()

                print(self.speech_intervals)
                if not (self.speech_intervals and (self.speech_intervals[-1][1] > duration*run_num+4.3 and self.speech_intervals[-1][1] <= duration*run_num+5)):
                    print("breaking from the loop")
                    break
                run_num += 1
            if self.speech_intervals:
                print("Transcribing...")
                self.write_wav(frames = self.frames, filename = "listen.wav")
                head.run_all()