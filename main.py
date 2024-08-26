from classes.CyberMind import CyberMind
from classes.SpeechDetector import SpeechDetector
import threading

head = CyberMind(llm_model="bambucha/saiga-llama3")
detector = SpeechDetector() 

def main():
    print(id(head))
    thread = threading.Thread(target=detector.record_audio, args=(head,))
    thread.daemon = True
    thread.start()

    print("Daemon is running")
    while True:
        pass
 
if __name__ == "__main__":
    # main()
    head.run_all()
    

