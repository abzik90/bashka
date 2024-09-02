import pyaudio
import threading
import time
import wave
import numpy as np

class SpeechDetector:
    def __init__(self, sample_rate=16000, window_size=1024, max_delay = 2, duration = 4):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.duration = duration
        self.max_delay = max_delay
        self.frames, self.sums = [], []
        self.p = pyaudio.PyAudio()

    def write_wav(self, frames, filename="speech.wav"):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    # Function to convert byte data to normalized numpy array
    def bytes_to_normalized(self, raw_data):
        audio_data = np.frombuffer(raw_data, dtype=np.int16)
        audio_data = audio_data.astype(np.float32) / 32768

        return audio_data

    def record_audio(self, head, buffer_size = 10):
        stream = self.p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.sample_rate,
                            input=True,
                            frames_per_buffer=self.window_size)

        print("Recording... Press Ctrl+C to stop.")
        
        # max_frames will be like a frame buffer limit
        max_frames = int(self.sample_rate / self.window_size * self.duration) # Calculate the number of frames for n seconds
        following_start = int(self.sample_rate / self.window_size * (self.duration-self.max_delay))
        buffer = []
        audio_data = []
        start_time, threshold = 0, 0

        try:
            while True:
                # frame_start = time.time()
                
                raw_data = stream.read(self.window_size)
                # print(time.time() - frame_start)

                # ~7ms
                normalized_data = self.bytes_to_normalized(raw_data)

                # 5-7 * 10^-5 s
                self.frames.append(raw_data)
                buffer.append(np.sum(normalized_data ** 2))

                # 3 * 10^-6 s < t < 0.0005 s
                # slide the window right, e.g subtract leftmost and add rightmost element
                if len(buffer) >= buffer_size:
                    current_sum = np.sum(buffer) if len(buffer) == buffer_size else self.sums[-1] - buffer.pop(0) + buffer[-1]
                    self.sums.append(current_sum)

                    threshold = np.median(self.sums)/buffer_size
                    print(threshold)
                # record if volume is higher than the threshold or till timeout after the last activation
                # 6-7 * 10^-6 s
                if buffer[-1] > threshold:
                    start_time = time.time()
                if threshold > 0.5 and time.time() - start_time < self.max_delay:
                    print("recording...")
                    audio_data.append(self.frames[-1])
                elif audio_data and len(audio_data)/(self.sample_rate / self.window_size) > self.max_delay:
                    print(f"A new file has been saved with length {len(audio_data)/(self.sample_rate / self.window_size)} seconds")
                    self.write_wav(audio_data)
                    head.run_all()
                    audio_data = []
                # 2 * 10^-6 s
                if len(self.frames) > max_frames: 
                    buffer = buffer[following_start:]
                    self.frames = self.frames[following_start:]
                    self.sums = self.sums[following_start:]
                    
        except KeyboardInterrupt:
            print("Recording stopped by user.")

        stream.stop_stream()
        stream.close()

    def record_in_thread(self, head):
        thread = threading.Thread(target=self.record_audio, args = (head,))
        thread.daemon = True
        thread.start()
        return thread
    
    def __del__(self):
        self.p.terminate()
        
if __name__ == "__main__":
    # Start recording in a daemon thread
    sd = SpeechDetector()
    record_thread = sd.record_in_thread()

    try:
        while record_thread.is_alive():
            pass
    except KeyboardInterrupt:
        print("Main thread interrupted. Exiting...")
