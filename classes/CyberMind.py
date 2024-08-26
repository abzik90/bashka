import asyncio
from faster_whisper import WhisperModel
from ollama import AsyncClient 
import sounddevice as sd
from TTS.api import TTS

DEVICE = "cuda" # if torch.cuda.is_available() else "cpu"
TRANSCRIPTION_FILE = "speech.wav"

class CyberMind:
    def __init__(self, model_size = "large-v3", llm_model = "llama3", tts_model = "ru_RU-dmitri-medium.onnx", tts_config = "ru_RU-dmitri-medium.onnx.json"):
        """
        Constructor for initializing the Voice Assistant instance.
        Utilizes CUDA for Faster-whisper local instance

        Args:
            api_key (str): The API key required for authentication with the OpenAI API.
            audio_filename (str): The location of the temporary audio file to be transcribed.
        """
        # self.transcription_model = WhisperModel(model_size, device=DEVICE, compute_type="int8_float16") # int8_float16
        self.llm_model = llm_model
        self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

    def print_response(self, response):
        print(response, end="\n", flush=True)

    def tts(self, response):
        print(response, end="\n", flush=True)
        wav = self.tts_model.tts(text=response, speaker_wav="./speech.wav", language="ru", speed=1.5)
        sd.play(wav, samplerate=22050)
        sd.wait()  # Wait until the audio is finished playing

    def transcribe(self, lang_code = "ru"):
        """
        Local Faster-Whisper API Transcription method.
        Args:
            lang_code (str): 2 character language code for transcription(Russian by default)
        Returns:
            str: Transcribed text from the audio file
        """
        segments, info = self.transcription_model.transcribe(TRANSCRIPTION_FILE, beam_size=5, language=lang_code)
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        transcribed = (segment.text for segment in segments)
        return " ".join(transcribed)
             
    async def send_prompt(self, textmessage, passed_function = print_response):
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
        async for part in await AsyncClient().chat(model=self.llm_model, messages=[message], stream=True):
            buffer += part["message"]["content"]
            # response += part["message"]["content"]
            # Split the response into chunks of 50 or more characters, ensuring each chunk ends with whitespace
            while len(buffer) >= 100:
                cutoff = buffer.rfind(' ', 0, 100)
                cutoff = cutoff if cutoff != -1 else 100
                passed_function(buffer[:cutoff].rstrip())
                buffer = buffer[cutoff:].lstrip()
        passed_function(buffer) if buffer else None
        # passed_function(response)
    def run_all(self):
        # transcribed_text = self.transcribe()
        transcribed_text = "Расскажи мне анекдот про сталкера в пару предложений"
        print("Transcribed:", transcribed_text)
        # transcribed_text = "привет, как дела?"
        print("Generated:")
        asyncio.run(self.send_prompt(transcribed_text, self.tts))
        print("="*40)
    
    def stop(self):
        asyncio.run(self.send_prompt("/bye"))
        
        