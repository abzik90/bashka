from classes.CyberMind import CyberMind
import os
import time

head = CyberMind(os.getenv("OPENAI_API_KEY"), "temp.mp3")
# Configure OpenAI API

print(os.getenv("OPENAI_API_KEY"))

if __name__ == "__main__":
   start_time = time.time()
   deltas = head.send_prompt()
   for change in deltas:
      print(change, end="", flush=True)
   print(f"\nOverall execution time: {time.time() - start_time}\n")
   # print(head.send_prompt())