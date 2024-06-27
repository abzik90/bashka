import numpy as np
import librosa
import matplotlib.pyplot as plt

# Load the audio file
file_path = 'check.wav'
y, sr = librosa.load(file_path, sr=None)
print(f"y:{len(y)} sr: {sr}")
# Confirm the duration of the audio file
audio_duration = librosa.get_duration(y=y, sr=sr)
print(f'Audio duration: {audio_duration:.2f} seconds')

# Function to detect silence
def detect_silence(y, sr, threshold=0.3, min_silence_duration=0.3):
    min_silence_samples = int(min_silence_duration * sr)
    abs_y = np.abs(y)
    silence_mask = abs_y < threshold
    silent_intervals = []
    current_silence_start = None
    for i in range(len(silence_mask)):
        if silence_mask[i]:
            if current_silence_start is None:
                current_silence_start = i
        else:
            if current_silence_start is not None:
                if (i - current_silence_start) >= min_silence_samples:
                    silent_intervals.append((current_silence_start, i))
                current_silence_start = None
    if current_silence_start is not None and (len(silence_mask) - current_silence_start) >= min_silence_samples:
        silent_intervals.append((current_silence_start, len(silence_mask)))
    return silent_intervals

# Detect silent intervals
silent_intervals = detect_silence(y, sr)
print("Silent intervals (in samples):", silent_intervals)

# Convert sample indices to time
silent_intervals_time = [(start / sr, end / sr) for start, end in silent_intervals]
print("Silent intervals (in seconds):", silent_intervals_time)

# Plot the audio waveform and silence intervals
plt.figure(figsize=(14, 6))
time = np.linspace(0, len(y) / sr, len(y))
plt.plot(time, y, label='Audio Signal')

# Highlight silence intervals
for (start, end) in silent_intervals_time:
    plt.axvspan(start, end, color='red', alpha=0.5, label='Silence' if start == silent_intervals_time[0][0] else "")

plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio Signal with Detected Silence Intervals')
plt.legend()
plt.show()
