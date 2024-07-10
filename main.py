from classes.CyberMind import CyberMind
import asyncio

head = CyberMind(llm_model="bambucha/saiga-llama3")


def main():
    try:
        head.run_all()
        head.stop()
    except KeyboardInterrupt:
        head.stop()

if __name__ == "__main__":
    main()
    

