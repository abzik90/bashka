import requests
import json

class StreamResponse:
    def __init__(self, url = "http://localhost:1234/v1/chat/completions") -> None:
        self.url = url
        self.system_message = "Ты русскоязычный голосовой ассистент. Ты играешь в роли комика, который вечно подкалывает и обидно подшучивает над собеседником. Каждое твое сообщение должно соопровождаться словом 'ананас'"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.params = {
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": True
        }

    def chat(self, user_message):
        data = {**{
            "messages" : [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ],
        }, **self.params}
        response = requests.post(self.url, headers=self.headers, json=data, stream=True)

        for line in response.iter_lines():
            if line:
                # Decode the response line
                decoded_line = line.decode('utf-8')
                
                # Remove the 'data: ' prefix if present
                if decoded_line.startswith("data: "):
                    decoded_line = decoded_line[len("data: "):]
                
                # Parse the JSON content
                try:
                    json_data = json.loads(decoded_line)
                    # Extract and print the 'content' if it exists
                    content = json_data.get("choices", [{}])[0].get("delta", {}).get("content")
                    if content:
                        yield(content)
                        # print(content, end= "")
                except json.JSONDecodeError:
                    continue