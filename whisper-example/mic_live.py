import pyaudio
from faster_whisper import WhisperModel
import threading
import wave
import time

# Parameters
SAMPLE_RATE = 16000  # Sample rate for recording
CHUNK_DURATION = 2.5  # Duration of each chunk in seconds
CHUNK_SIZE = 1024  # Buffer size
CHANNELS = 1  # Mono audio

# Initialize the Whisper model
model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def record_audio(p, stream):
    """Capture audio from the microphone in chunks and save to a WAV file."""
   
    print("Recording...")
    frames = []
    try:
        for _ in range(int(SAMPLE_RATE * CHUNK_DURATION / CHUNK_SIZE)):
            audio_data = stream.read(CHUNK_SIZE)
            frames.append(audio_data)
    except KeyboardInterrupt:
        print("Recording stopped by user.")

    # Save the recorded audio to a WAV file
    with wave.open("temp.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio():
    """Transcribe audio chunks from the queue."""
    # Transcribe audio chunk
    segments, _ = model.transcribe("temp.wav", beam_size=5, language="ru")
    transcription = " ".join(segment.text for segment in segments)
    # Print the transcription
    print("Transcription:", transcription)

if __name__ == "__main__":
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)
    try:
        while True:
            record_audio(p, stream)
            transcribe_audio()
    except KeyboardInterrupt:
        print("Terminated by the user")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()