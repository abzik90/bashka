import asyncio
from faster_whisper import WhisperModel
from ollama import AsyncClient 

TRANSCRIPTION_FILE = "temp.mp3"

class CyberMind:
    def __init__(self, model_size = "large-v3", llm_model = "llama3"):
        """
        Constructor for initializing the Voice Assistant instance.
        Utilizes CUDA for Faster-whisper local instance

        Args:
            api_key (str): The API key required for authentication with the OpenAI API.
            audio_filename (str): The location of the temporary audio file to be transcribed.
        """
        self.transcription_model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
        self.llm_model = llm_model

    def print_response(response):
        # print(response, end="\n", flush=True)
        print(response)
    def tts(response):
        pass

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
        async for part in await AsyncClient().chat(model=self.llm_model, messages=[message], stream=True):
            buffer += part["message"]["content"]
            # Split the response into chunks of 50 or more characters, ensuring each chunk ends with whitespace
            while len(buffer) >= 50:
                cutoff = buffer.rfind(' ', 0, 50)
                cutoff = cutoff if cutoff != -1 else 50
                passed_function(buffer[:cutoff].rstrip())
                buffer = buffer[cutoff:].lstrip()
        passed_function(buffer) if buffer else None
    def run_all(self):
        transcribed_text = self.transcribe()
        print(transcribed_text)
        # transcribed_text = "привет, как дела?"
        asyncio.run(self.send_prompt(transcribed_text))
        print("="*40)
    
    def stop(self):
        asyncio.run(self.send_prompt("/bye"))
        
        