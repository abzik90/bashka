import openai
import threading
from .EventHandler import EventHandler
from .HeadListen import HeadListen
import os

semaphore = threading.Semaphore(1)

class CyberMind:
    def __init__(self, api_key, audio_filename):
        """
        Constructor for initializing the class instance.

        Args:
            api_key (str): The API key required for authentication with the OpenAI API.
            audio_filename (str): The location of the temporary audio file to be transcribed.
        """
        openai.api_key = api_key
        self.audio_filename = audio_filename
        self.client = openai.OpenAI()
        self.assistant = self.client.beta.assistants.create(
                    instructions=f"Ты являешься голосовым ассистентом внутри гуманойдного робота. Тебе будут предоставляться транскрипты аудиофайлов полученные по whisper. Твоя задача коротко и ясно отвечать пользователю на его запросы в 3-4 предложениях",
                    name="bashka",
                    tools=[{"type": "code_interpreter"}],
                    model="gpt-4o",
        )
        self.thread = self.client.beta.threads.create()
        self.output_counter = 1

    def transcribe(self):
        """
        Whisper API Transcription method.

        Returns:
            str: Transcribed text from the audio file
        """
        audio_file= open(self.audio_filename, "rb")
        return self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )

    def send_prompt(self):
        """
        OpenAI API for response generation.

        Yields:
            str: Streams the response text generated from the OpenAI API response
        Returns:
            str: Full response
        """
        transcribed_text = self.transcribe()
        print("Transcribed text:", transcribed_text)
        message = self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = "user",
            content = f"Ответь на последующую транскрипцию: {transcribed_text}",
        )

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            event_handler=EventHandler(),
        ) as stream:
            # stream.until_done()
            for event in stream:
                if event.event == 'thread.message.delta':
                    yield event.data.delta.content[0].text.value

    def listens(self):
        """
        Listen for spacebar key press(hold) and release
        Record audio during the key hold

        Writes temp.mp3 file
        """
        head_listener = HeadListen(self.audio_filename)
        head_listener.listener()
    
    def text_to_speech(self, text, thread_id):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text,
        )
         # Define output file path
        output_file = os.path.join("outputs", f"{thread_id}.mp3")
        response.stream_to_file(output_file)
        self.output_counter += 1