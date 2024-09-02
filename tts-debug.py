from ollama import AsyncClient 
from faster_whisper import WhisperModel
from TTS.api import TTS
import sounddevice as sd
import asyncio 

DEVICE = "cuda"
llm_model = "bambucha/saiga-llama3"
TRANSCRIPTION_FILE = "./sources/source-igor.wav"

transcription_model = WhisperModel("small", device=DEVICE, compute_type="int8_float16") # int8_float16
print("Whisper model initialized successfully")
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
print("Text-to-speech model initialized successfully")

def transcribe(lang_code = "ru"):
    """
    Local Faster-Whisper API Transcription method.
    Args:
        lang_code (str): 2 character language code for transcription(Russian by default)
    Returns:
        str: Transcribed text from the audio file
    """
    segments, info = transcription_model.transcribe(TRANSCRIPTION_FILE, beam_size=5, language=lang_code)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcribed = (segment.text for segment in segments)
    return " ".join(transcribed)

async def send_prompt(textmessage):
        """
        Ollama response generation. Will run the function passed with the generated response

        Args:
            textmessage (str): Text message as prompt
            passed_function (function, optional): A function to handle the generated response.
                Defaults to print_response if not provided.
        """

        message = {
            "role": "user",
            "content": textmessage
        }
        
        buffer = ""
        response = ""
        async for part in await AsyncClient().chat(model=llm_model, messages=[message], stream=True):
            buffer += part["message"]["content"]
            # response += part["message"]["content"]
            # Split the response into chunks of 50 or more characters, ensuring each chunk ends with whitespace
            while len(buffer) >= 100:
                cutoff = buffer.rfind(' ', 0, 100)
                cutoff = cutoff if cutoff != -1 else 100
                tts(buffer[:cutoff].rstrip())
                buffer = buffer[cutoff:].lstrip()
        tts(buffer) if buffer else None
        # passed_function(response)
def tts(response):
    print(response, end="\n", flush=True)
    wav = tts_model.tts(text=response, speaker_wav="./speech.wav", language="ru", speed=1.5)
    
    sd.play(wav, samplerate=22050)
    # .lipsync()
    sd.wait()  # Wait until the audio is finished playing

def run_all():
    transcribed_text = transcribe()
    # transcribed_text = "Расскажи мне анекдот про сталкера в пару предложений"
    print("Transcribed:", transcribed_text)
    # tts(transcribed_text)
    print("Generated:")
    asyncio.run(send_prompt(transcribed_text))
    print("="*40)

if __name__ == "__main__":
    run_all()