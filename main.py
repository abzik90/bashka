from classes.CyberMind import CyberMind
# from classes.ThreadFlags import ThreadFlags
import os, threading, time
from playsound import playsound

TEMP_MP3_FILE = "temp.mp3"
head = None
semaphore = threading.Semaphore(1)

def sequential_playback(thread_id):
    semaphore.acquire()
    playsound(os.path.join("outputs", f"{thread_id}.mp3"))
    semaphore.release()

if __name__ == "__main__":
    print("Press and hold the space bar to start recording.")
    print("Release the space bar to stop recording.")
    
    head = CyberMind(os.getenv("OPENAI_API_KEY"), TEMP_MP3_FILE)
    
    while True:
        print("="*60)
        head.listens()

        deltas = head.send_prompt()
        response = ""
        threads = []
        thread_id = 1

        for change in deltas:
            print(change, end="", flush=True)
            response += change
            if len(response) > 50:
                t = threading.Thread(target=head.text_to_speech, args=(response, thread_id))
                t.start()
                threads.append(t)
                response = ""
                if thread_id > 1:
                    if thread_id-1 == 1:
                        time.sleep(2)
                    y = threading.Thread(target=sequential_playback, args=(thread_id-1,))
                    y.start()
                    y.join()

                thread_id += 1
        if response:
            t = threading.Thread(target=head.text_to_speech, args=(response, thread_id))
            t.start()
            threads.append(t)
                    
        y = threading.Thread(target=sequential_playback, args=(thread_id-1,))
        y.start()
        y.join()

        y = threading.Thread(target=sequential_playback, args=(thread_id,))
        y.start()
        y.join()

        for t in threads:
            t.join()
            
       
        head.output_counter = 1
        print("="*60)
