import requests
import json

url = "http://localhost:1234/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
data = {
    "messages": [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "How do I init and update a git submodule?"}
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)

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
                print(content, end= "")
        except json.JSONDecodeError:
            continue
