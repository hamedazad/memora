import speech_recognition as sr
import pyttsx3
from typing import Tuple

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        
        # Configure text-to-speech engine
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def listen_for_speech(self, timeout: int = 5) -> Tuple[bool, str]:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                return True, text
        except Exception as e:
            return False, f"Error: {e}"
    
    def speak_text(self, text: str) -> bool:
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            return False

voice_service = VoiceService() 