import pyaudio
import numpy as np
from faster_whisper import WhisperModel

model_size = "large-v3"
# Initialize the Whisper model
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Parameters
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Format of audio stream
CHANNELS = 1  # Number of audio channels
RATE = 16000  # Sample rate (samples per second)
SILENCE_THRESHOLD = 500  # Threshold for considering a chunk as silence
SILENCE_FRAMES = 30  # Number of consecutive silent frames to trigger the function
KEYPHRASES = ["Amina", "Амина", "амина"]  # List of keyphrases to detect

# Initialize PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Variables to keep track of transcription and silence detection
buffer = []
silence_count = 0
collecting = False
collected_text = ""

def transcribe_audio(buffer):
    """Transcribe the audio buffer using the Whisper model."""
    audio_data = np.frombuffer(b''.join(buffer), dtype=np.int16)
    segments, info = model.transcribe(audio_data, beam_size=5, language="ru")
    return ' '.join(segment.text for segment in segments)

def is_silent(audio_chunk):
    """Check if the audio chunk is silent."""
    return np.max(np.frombuffer(audio_chunk, dtype=np.int16)) < SILENCE_THRESHOLD

def contains_keyphrase(text, keyphrases):
    """Check if the transcribed text contains any of the keyphrases."""
    return any(keyphrase in text for keyphrase in keyphrases)

try:
    print("Yap:")
    while True:
        print(collected_text)
        # Read audio chunk from stream
        audio_chunk = stream.read(CHUNK)
        buffer.append(audio_chunk)

        if is_silent(audio_chunk):
            silence_count += 1
        else:
            silence_count = 0

        # If we've detected enough silence and were collecting text, process the buffer
        if silence_count >= SILENCE_FRAMES:
            if collecting:
                # Transcribe the audio buffer
                transcription = transcribe_audio(buffer)
                collected_text += transcription + " "
                buffer = []  # Clear buffer after processing

                # Trigger the function (e.g., print the collected text)
                print("Collected text:", collected_text.strip())

                # Reset variables
                collecting = False
                collected_text = ""
                silence_count = 0
        else:
            # Transcribe the audio buffer on the fly
            transcription = transcribe_audio(buffer)
            buffer = []  # Clear buffer after processing

            if contains_keyphrase(transcription, KEYPHRASES):
                collecting = True
                collected_text = transcription
            elif collecting:
                collected_text += transcription + " "
except KeyboardInterrupt:
    # Stop the stream gracefully
    print("\nStopping transcription.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
