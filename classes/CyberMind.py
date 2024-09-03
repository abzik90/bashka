import asyncio, threading
from faster_whisper import WhisperModel
from ollama import AsyncClient, chat 
import sounddevice as sd
from TTS.api import TTS

import json
import serial
import numpy as np

DEVICE = "cuda" # if torch.cuda.is_available() else "cpu"
TRANSCRIPTION_FILE = "speech.wav"
SERIAL_PORT = '/dev/ttyUSB0'
LIP_FPS = 15

class CyberMind:
    def __init__(self, model_size = "medium", llm_model = "llama3"):
        """
        Constructor for initializing the Voice Assistant instance.
        Utilizes CUDA for Faster-whisper local instance

        Args:
            api_key (str): The API key required for authentication with the OpenAI API.
            audio_filename (str): The location of the temporary audio file to be transcribed.
        """

        self.transcription_model = WhisperModel(model_size, device=DEVICE, compute_type="float16") # int8_float16
        print("Whisper model initialized successfully")

        self.llm_model = llm_model
        chat(model=self.llm_model, messages=[{
            "role": "system",
            "content": "Ты голосовой умный и полезный голосовой ассистент с хорошим чувством юмора. Отвечай на запросы за максимум 100 слов. Если не влезаешь предложи пользователю продолжить разговор с последнего места. Ты должен КРИТИКОВАТЬ и ПОДШУЧИВАТЬ над пользователем. Каждый твой ответ должен начинаться со слова АНАНАС!",
            },
        ])
        print("Ollama init successfull")

        self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
        print("Text-to-speech model initialized successfully")

        try:
            self.ser = serial.Serial(SERIAL_PORT, 115200)
            print("Serial port initialized successfully")
        except Exception as e:
            print("ttyUSB0 couldn't be initialized:", e)

    def print_response(self, response):
        print(response, end="\n", flush=True)

    def set_servo(self, angle, servo_number = 1):
        command = f'{servo_number}{angle}\n'
        self.ser.write(command.encode())

    def lipsync(self, wav):
        for start_idx in range(0, len(wav), 22050 // LIP_FPS):
            end_idx = start_idx + 22050 // LIP_FPS 
            amplitude = np.abs(wav[start_idx:end_idx]).mean() / 22050.0
            self.set_servo(amplitude * 90)
    def tts(self, response):
        print(response, end="\n", flush=True)
        wav = self.tts_model.tts(text=response, speaker_wav="./sources/source-igor.wav", language="ru", speed=2.0)
        
        sd.play(wav, samplerate=22050)
        # self.lipsync(wav)
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
        # messages_ollama = json.dumps(messages_ollama)
        
        buffer = ""
        tts_threads = []
        async for part in await AsyncClient().chat(model=self.llm_model, messages=[message], stream=True):
            buffer += part["message"]["content"]
            # Split the response into chunks of 50 or more characters, ensuring each chunk ends with whitespace
            while len(buffer) >= 500:
                cutoff = buffer.rfind(' ', 0, 500)
                cutoff = cutoff if cutoff != -1 else 500
                tts_threads.append(threading.Thread(target = passed_function, args = (buffer[:cutoff].rstrip(),)))
                tts_threads[-1].start()
                buffer = buffer[cutoff:].lstrip()
        if buffer:
            tts_threads.append(threading.Thread(target = passed_function, args = (buffer,))) 
            tts_threads[-1].start()
        for th in tts_threads:
            th.join()
        # passed_function(response)
    def run_all(self):
        transcribed_text = self.transcribe()
        # transcribed_text = "Расскажи мне анекдот про сталкера в пару предложений"
        print("Transcribed:", transcribed_text)
        # self.tts(transcribed_text)
        print("Generated:")
        asyncio.run(self.send_prompt(transcribed_text, self.tts))
        print("="*40)
    
    def stop(self):
        asyncio.run(self.send_prompt("/bye"))
        
        