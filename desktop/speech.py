"""
JARVIS Speech Module
- listen(): record audio from microphone and transcribe with Vosk
- speak(text): text-to-speech via pyttsx3
"""
import os
import json
import wave
import queue
import threading
# import pyaudio  # Deferred
# import pyttsx3  # Deferred
# from vosk import Model, KaldiRecognizer  # Deferred
import time
import config

# ─── TTS Engine ────────────────────────────────────────────────────────────────

_tts_engine = None
_tts_lock = threading.Lock()

def _get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", config.TTS_RATE)
        _tts_engine.setProperty("volume", config.TTS_VOLUME)
        # Try to set a good voice (prefer male deep voice for JARVIS feel)
        voices = _tts_engine.getProperty("voices")
        selected_voice = voices[0] # Fallback
        for voice in voices:
            if "male" in voice.name.lower() or "david" in voice.name.lower():
                selected_voice = voice
                break
        
        _tts_engine.setProperty("voice", selected_voice.id)
        print(f"[JARVIS] 🔊 TTS Voice: {selected_voice.name}")
    return _tts_engine


def _is_hindi(text: str) -> bool:
    """Simple check for Hindi characters (Devanagari script range)."""
    return any('\u0900' <= char <= '\u097f' for char in text)


def speak(text: str) -> None:
    """Speak the given text aloud. Uses gTTS for Hindi and pyttsx3 for English."""
    if not text:
        return

    # Check for Hindi text
    if _is_hindi(text):
        from gtts import gTTS
        from playsound import playsound
        import tempfile
        
        try:
            print(f"[JARVIS] ▶ (Hindi/gTTS) {text}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_name = fp.name
            
            tts = gTTS(text=text, lang='hi')
            tts.save(temp_name)
            playsound(temp_name)
            os.remove(temp_name)
            return
        except Exception as e:
            print(f"[JARVIS] gTTS (Hindi) Error: {e}")
            # Fallback to pyttsx3 (even if it sounds bad)

    import pyttsx3
    try:
        with _tts_lock:
            print(f"[JARVIS] ▶ {text}")
            # Re-init engine every time for better reliability on Windows/Bluetooth
            engine = pyttsx3.init()
            engine.setProperty("rate", config.TTS_RATE)
            engine.setProperty("volume", config.TTS_VOLUME)
            
            voices = engine.getProperty("voices")
            selected_voice = voices[0]
            for voice in voices:
                if "male" in voice.name.lower() or "david" in voice.name.lower():
                    selected_voice = voice
                    break
            
            engine.setProperty("voice", selected_voice.id)
            engine.say(text)
            engine.runAndWait()
            # Clean up engine resources
            del engine
    except Exception as e:
        print(f"[JARVIS] Speaker error: {e}")
        print(f"[JARVIS] (Fallback text only) ▶ {text}")


# ─── Speech Recognition ────────────────────────────────────────────────────────

_vosk_model: Model | None = None


def get_vosk_model():
    """Public accessor for the Vosk model (loads if not already loaded)."""
    global _vosk_model
    if _vosk_model is None:
        from vosk import Model
        model_path = config.VOSK_MODEL_PATH
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Vosk model not found at '{model_path}'.\n"
                "Download a model from https://alphacephei.com/vosk/models\n"
                "and extract it to the desktop/ folder."
            )
        print(f"[JARVIS] 🧠 Loading speech model from: {os.path.basename(model_path)}...")
        _vosk_model = Model(model_path)
        print("[JARVIS] ✅ Model ready.")
    return _vosk_model


def preload_model():
    """Manually trigger model loading without listening."""
    get_vosk_model()


def _transcribe_cloud(filename: str) -> str | None:
    """Send audio file to backend for Whisper transcription."""
    import requests
    try:
        with open(filename, "rb") as f:
            files = {"file": (os.path.basename(filename), f, "audio/wav")}
            response = requests.post(
                f"{config.BACKEND_URL}/api/transcribe",
                files=files,
                headers={"Authorization": f"Bearer {config.JARVIS_API_TOKEN}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("text")
    except Exception as e:
        print(f"[JARVIS] Cloud STT error: {e}")
        return None


def listen(max_duration: int = 15) -> str:
    """
    Record audio from the default microphone until silence is detected
    or max_duration is reached. Supports local (Vosk) and cloud (Whisper).
    """
    from pvrecorder import PvRecorder
    import struct
    import math
    import tempfile
    import wave

    recorder = PvRecorder(device_index=config.MIC_INDEX, frame_length=512)
    recorder.start()

    print(f"[JARVIS] 🎤 Listening... (max {max_duration}s)")
    
    start_time = time.time()
    last_voice_time = time.time()
    has_started_talking = False
    all_frames = []
    
    try:
        while time.time() - start_time < max_duration:
            pcm = recorder.read()
            all_frames.extend(pcm)
            
            # Simple energy calculation (RMS)
            sum_squares = sum(x*x for x in pcm)
            rms = math.sqrt(sum_squares / len(pcm))
            
            # If noise level is above threshold, update last_voice_time
            if rms > config.SILENCE_THRESHOLD:
                last_voice_time = time.time()
                has_started_talking = True
            
            # Stop if silence lasts too long AFTER talking has started
            if has_started_talking and (time.time() - last_voice_time > config.SILENCE_DURATION_SECONDS):
                print("[JARVIS] 🤫 Silence detected, stopping capture.")
                break
    finally:
        recorder.stop()
        recorder.delete()

    # Process audio
    if not all_frames:
        return ""

    if config.USE_CLOUD_STT:
        # Save to temp WAV and send to cloud
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            temp_wav = fp.name
        
        with wave.open(temp_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(16000)
            wf.writeframes(struct.pack("h" * len(all_frames), *all_frames))
        
        print(f"[JARVIS] ✨ Sending to cloud for perfect accuracy...")
        text = _transcribe_cloud(temp_wav)
        os.remove(temp_wav)
        
        if text is not None:
            print(f"[JARVIS] 📝 Heard (Cloud): '{text}'")
            return text
        print("[JARVIS] ⚠️ Cloud STT failed, falling back to local...")

    # Fallback to local Vosk
    from vosk import KaldiRecognizer
    model = get_vosk_model()
    recognizer = KaldiRecognizer(model, 16000)
    data = struct.pack("h" * len(all_frames), *all_frames)
    recognizer.AcceptWaveform(data)
    
    result = json.loads(recognizer.FinalResult())
    text = result.get("text", "").strip()
    print(f"[JARVIS] 📝 Heard (Local): '{text}'")
    return text
