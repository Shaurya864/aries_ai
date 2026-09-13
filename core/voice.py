"""
Voice Subsystems for Aries AI (Phase 4).
Handles Speech-to-Text (STT) via microphone and Text-to-Speech (TTS) via pyttsx3.
"""

from __future__ import annotations
import threading
import pyttsx3
import speech_recognition as sr

# Initialize TTS engine safely
_tts_engine = None
_tts_lock = threading.Lock()

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        try:
            _tts_engine = pyttsx3.init()
            # Optional: Adjust speech rate or volume
            _tts_engine.setProperty('rate', 175)
        except Exception as e:
            print(f"[TTS Init Error]: {e}")
    return _tts_engine

def speak_text(text: str):
    """
    Reads text aloud asynchronously using pyttsx3 wrapped in a thread lock 
    to prevent engine overlap crashes.
    """
    def _run_tts():
        with _tts_lock:
            engine = get_tts_engine()
            if engine:
                engine.say(text)
                engine.runAndWait()

    # Run on a background thread so it doesn't block the UI
    threading.Thread(target=_run_tts, daemon=True).start()


def listen_to_microphone() -> str:
    """
    Listens to microphone input via SpeechRecognition and returns transcribed text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[VOICE] Listening for speech...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Listen with a timeout
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("[VOICE] Processing speech...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "[Error: Could not understand audio]"
        except sr.RequestError as e:
            return f"[Error connecting to speech service: {e}]"