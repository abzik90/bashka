from faster_whisper import WhisperModel
import time

model_size = "large-v1"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe(file, lang_code = "ru"):
    """
    Local Faster-Whisper API Transcription method.
    Args:
        lang_code (str): 2 character language code for transcription(Russian by default)
    Returns:
        str: Transcribed text from the audio file
    """
    segments, info = model.transcribe(file, beam_size=5, language="ru")
    
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcribed = (segment.text for segment in segments)
    print(" ".join(transcribed))
    return " ".join(transcribed)
    

transcribe("source-aga.wav")
time.sleep(7)
transcribe("source-igor.wav")
time.sleep(7)
transcribe("source-asset.wav")