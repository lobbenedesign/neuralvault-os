import os
import torch
import logging
from faster_whisper import WhisperModel
import pyttsx3
import threading
import queue

logger = logging.getLogger("NeuralVault-Voice")

class SovereignVoiceEngine:
    """
    🎙️ [SOVEREIGN VOICE ENGINE]
    Gestisce l'interazione vocale naturale tramite Whisper (STT) e pyttsx3 (TTS).
    Tutto il processamento avviene localmente.
    """
    def __init__(self, model_size="tiny", device="cpu"):
        self.device = device
        # Caricamento Whisper (Tiny per massime performance in real-time)
        logger.info(f"🎙️ Caricamento Whisper ({model_size}) su {device}...")
        self.stt_model = WhisperModel(model_size, device=device, compute_type="int8")
        
        # Inizializzazione TTS
        self.tts_engine = pyttsx3.init()
        self._setup_tts_voices()
        
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        
        # Avvio thread dedicato per il parlato (evita blocchi dell'API)
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

    def _setup_tts_voices(self):
        voices = self.tts_engine.getProperty('voices')
        # Cerchiamo una voce italiana se disponibile
        for voice in voices:
            if "italian" in voice.name.lower() or "it_IT" in voice.id:
                self.tts_engine.setProperty('voice', voice.id)
                break
        self.tts_engine.setProperty('rate', 175) # Velocità naturale

    def transcribe(self, audio_path: str) -> str:
        """Trascrive un file audio in testo."""
        segments, info = self.stt_model.transcribe(audio_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def speak(self, text: str):
        """Aggiunge un testo alla coda del parlato."""
        self.speech_queue.put(text)

    def _tts_worker(self):
        while True:
            text = self.speech_queue.get()
            if text is None: break
            
            self.is_speaking = True
            logger.info(f"🔊 Speaking: {text[:50]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            self.speech_queue.task_done()

    def stop(self):
        self.speech_queue.put(None)
