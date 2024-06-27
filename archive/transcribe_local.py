from faster_whisper import WhisperModel

model_size = "large-v3"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def transcribe(filename = "temp.mp3"):
    segments, info = model.transcribe(filename, beam_size=5, language="ru")
    for segment in segments:
        yield(segment.text) 

# transcription = transcribe()
# for text in transcription:
#     print(text)