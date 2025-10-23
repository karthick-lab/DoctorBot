import pyttsx3
import threading

def speak_bilingual(text):
    def speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=speak).start()