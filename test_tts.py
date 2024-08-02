# from TTS.utils.manage import ModelManager
# from TTS.utils.synthesizer import Synthesizer

# path = "/home/nurbol/.local/lib/python3.10/site-packages/TTS/.models.json"

# model_manager = ModelManager(path)
# model_path, config_path, model_item = model_manager.download_model("tts_models/multilingual/multi-dataset/xtts_v1.1")
# print(model_path, config_path)
# synthesizer = Synthesizer(
#     tts_checkpoint=model_path,
#     tts_config_path=config_path
# )

# text = "This is a test TTS speech generated from Bark TTS model. Барк является мультилингуальной моделью озвучки текста в голос"
# output = synthesizer.tts(text)
# synthesizer.save_wav(output, "bark.wav")

# import torch
from TTS.api import TTS
import sounddevice as sd

# Get device
device = "cuda" # if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to("cuda")

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
# wav = tts.tts(text="", speaker_wav="./source.wav", language="en")
# Text to speech to a file
text="Технология синтеза речи (TTS) преобразует текстовую информацию в естественное звучание речи, позволяя компьютерам и другим устройствам произносить текст вслух. Она широко используется в голосовых помощниках, навигационных системах и приложениях для улучшения доступности информации."
# tts.tts_to_file(, speaker_wav="./source.wav", language="ru", file_path="output1.wav")

wav = tts.tts(text=text, speaker_wav="./sources/source.wav", language="ru", speed=1.5)

# Play the speech
sd.play(wav, samplerate=22050)
sd.wait()  # Wait until the audio is finished playing
