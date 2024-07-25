import numpy as np
import librosa

class ListenerHead:
    def __init__(self, y, sr, noise_factor=1.5, min_noise_duration=2):
        self.y = y
        self.sr = sr
        self.noise_factor = noise_factor
        # detect noise for 2s(default) or more
        self.min_noise_duration = min_noise_duration
        self.dynamic_threshold = 0
    def compute_dynamic_threshold(self):
        """
            Function to compute a dynamic threshold based on background noise 
            using mean absolute amplitude as the background noise level

            Assigns:
                int: self.dynamic_threshold
        """
        self.dynamic_threshold = self.noise_factor * np.mean(np.abs(self.y))
        # For testing purposes
        print(f"Background noise level (mean): {self.dynamic_threshold / self.noise_factor}")
        print(f"Dynamic threshold: {self.dynamic_threshold}")

    # Function to detect noise using a dynamic threshold
    def detect_noise(self, y, sr):
        self.compute_dynamic_threshold()
        min_noise_samples = int(self.min_noise_duration * sr)
        abs_y = np.abs(y)
        noise_mask = abs_y > self.dynamic_threshold

        # Find the start and end points of noisy intervals
        silent_intervals = []
        silence_changes = np.diff(silence_mask.astype(int))
        silence_starts = np.where(silence_changes == 1)[0] + 1
        silence_ends = np.where(silence_changes == -1)[0] + 1

        # Handle cases where silence starts at the beginning or ends at the end
        if silence_mask[0]:
            silence_starts = np.insert(silence_starts, 0, 0)
        if silence_mask[-1]:
            silence_ends = np.append(silence_ends, len(silence_mask))

        # Filter out short silent intervals
        for start, end in zip(silence_starts, silence_ends):
            if (end - start) >= min_silence_samples:
                silent_intervals.append((start, end))
        
        return merge_close_intervals(silent_intervals, sr, min_gap_duration=0.1)

    # Post-processing step to merge close silent intervals
    def merge_close_intervals(silent_intervals, sr, min_gap_duration=0.1):
        min_gap_samples = int(min_gap_duration * sr)
        merged_intervals = []
        current_start, current_end = silent_intervals[0]

        for start, end in silent_intervals[1:]:
            if start - current_end <= min_gap_samples:
                # Merge the intervals
                current_end = end
            else:
                merged_intervals.append((current_start, current_end))
                current_start, current_end = start, end

        # Append the last interval
        merged_intervals.append((current_start, current_end))
        
        return merged_intervals

    # get silent intervals in seconds
    def get_silent_intervals(file_path):
        y, sr = librosa.load(file_path, sr=None)
        silent_intervals = detect_silence(y, sr, noise_factor=3)
        merged_silent_intervals_time = [(start / sr, end / sr) for start, end in merged_silent_intervals]


# Detect silent intervals
silent_intervals = detect_silence(y, sr, noise_factor=3)  # Adjust the noise_factor if needed
print("Silent intervals (in samples):", silent_intervals)

# Merge close silent intervals
# merged_silent_intervals = merge_close_intervals(silent_intervals, sr, min_gap_duration=0.1)
# print("Merged silent intervals (in samples):", merged_silent_intervals)

# Convert sample indices to time
merged_silent_intervals_time = [(start / sr, end / sr) for start, end in merged_silent_intervals]
print("Merged silent intervals (in seconds):", merged_silent_intervals_time)

# Plot the audio waveform and silence intervals
plt.figure(figsize=(14, 6))
time = np.linspace(0, len(y) / sr, len(y))
plt.plot(time, y, label='Audio Signal')

# Highlight silence intervals
for (start, end) in merged_silent_intervals_time:
    plt.axvspan(start, end, color='red', alpha=0.5, label='Silence' if start == merged_silent_intervals_time[0][0] else "")

plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio Signal with Detected Silence Intervals')
plt.legend()
plt.show()
