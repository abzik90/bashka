from pydub import AudioSegment
interval = [0.2786394557823129, 2.647074829931973]

# Load the MP3 file
audio = AudioSegment.from_mp3("temp.mp3")

# Define your time intervals (in milliseconds)
start_time = interval[0] * 1000  # convert seconds to milliseconds
end_time = interval[1] * 1000    # convert seconds to milliseconds

# Ensure end_time is within the actual duration of the audio
end_time = min(end_time, len(audio))

# Extract the segment between start_time and end_time
cropped_audio = audio[start_time:end_time]

# Export the cropped audio to a new MP3 file
cropped_audio.export("cropped_temp.mp3", format="mp3")

