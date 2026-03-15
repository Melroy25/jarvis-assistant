"""
JARVIS Desktop Client Configuration
Reads settings from environment variables (via .env file).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Backend API
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:3000")
JARVIS_API_TOKEN: str = os.getenv("JARVIS_API_TOKEN", "change-this-to-a-random-secret")

# Picovoice / Porcupine
PICOVOICE_ACCESS_KEY: str = os.getenv("PICOVOICE_ACCESS_KEY", "")

# Microphone configuration
MIC_INDEX: int = int(os.getenv("MIC_INDEX", "-1"))  # -1 for default

# Device identity
DEVICE_ID: str = os.getenv("DEVICE_ID", "desktop-1")

# Wake word configuration
WAKE_WORD_NAME: str = os.getenv("WAKE_WORD_NAME", "jarvis")
# Path to a custom .ppn file (optional)
WAKE_WORD_PATH: str = os.getenv("WAKE_WORD_PATH", "")
WAKE_WORD_SENSITIVITY: float = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))

# Audio recording duration (seconds) after wake word
COMMAND_LISTEN_SECONDS: int = int(os.getenv("COMMAND_LISTEN_SECONDS", "5"))

# Vosk model path (download from https://alphacephei.com/vosk/models)
VOSK_MODEL_PATH: str = os.getenv("VOSK_MODEL_PATH", "./vosk-model")

# Silence detection for commands
SILENCE_THRESHOLD: float = float(os.getenv("SILENCE_THRESHOLD", "100.0"))
SILENCE_DURATION_SECONDS: float = float(os.getenv("SILENCE_DURATION_SECONDS", "3.0"))

# TTS settings
TTS_RATE: int = int(os.getenv("TTS_RATE", "180"))   # words per minute
TTS_VOLUME: float = float(os.getenv("TTS_VOLUME", "1.0"))

# Speed & Accuracy optimizations
FAST_RESPONSE: bool = os.getenv("FAST_RESPONSE", "false").lower() == "true"
USE_CLOUD_STT: bool = os.getenv("USE_CLOUD_STT", "true").lower() == "true"
