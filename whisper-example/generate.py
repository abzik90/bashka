import openai
import os

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
print(os.getenv("OPENAI_API_KEY"))
client = openai.OpenAI()

assistant = client.beta.assistants.create(
        instructions=f"Ты являешься голосовым ассистентом внутри гуманойдного робота. Ты слышишь что говорит пользователь посредством алгоритма транскрибации на whisper, который будет тебе представлен в текстовом виде. Твоя задача коротко и ясно отвечать пользователю на его запросы в 3-4 предложениях",
        name="robodk_assist",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
)