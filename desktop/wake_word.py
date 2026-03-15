"""
JARVIS Wake Word Detection
Uses Picovoice Porcupine to listen for the "jarvis" keyword.

Built-in "jarvis" keyword is available by passing keyword_paths=None
and using the Keywords.JARVIS enum — available in pvporcupine >= 3.x
"""
# import pvporcupine  # Deferred
# from pvrecorder import PvRecorder  # Deferred
import os
import config


def start_listening(on_wake_word_callback):
    """
    Starts a blocking wake word detection loop.
    Calls `on_wake_word_callback()` whenever "Jarvis" is detected.
    Press Ctrl+C to stop.
    """
    import pvporcupine
    from pvrecorder import PvRecorder

    kwargs = {
        "access_key": config.PICOVOICE_ACCESS_KEY,
        "sensitivities": [config.WAKE_WORD_SENSITIVITY]
    }

    if config.WAKE_WORD_PATH and os.path.exists(config.WAKE_WORD_PATH):
        kwargs["keyword_paths"] = [config.WAKE_WORD_PATH]
    else:
        kwargs["keywords"] = [config.WAKE_WORD_NAME]

    porcupine = pvporcupine.create(**kwargs)

    import math
    import struct
    import time

    while True:
        try:
            print(f"[JARVIS] 🌙 Wake word engine started. Say '{config.WAKE_WORD_NAME}' to activate...")
            print(f"[JARVIS] Sample rate: {porcupine.sample_rate} | Frame length: {porcupine.frame_length}")
            
            try:
                recorder = PvRecorder(
                    frame_length=porcupine.frame_length,
                    device_index=config.MIC_INDEX,
                )
            except ValueError:
                print(f"[JARVIS] ⚠️ Device index {config.MIC_INDEX} not found. Falling back to default.")
                recorder = PvRecorder(
                    frame_length=porcupine.frame_length,
                    device_index=-1,
                )
                
            recorder.start()

            try:
                while True:
                    pcm = recorder.read()
                    
                    # Debug: show audio level
                    rms = math.sqrt(sum(x*x for x in pcm) / len(pcm))
                    level = int(rms / 10)
                    bar = "#" * min(level, 50)
                    print(f"\r[AUDIO] {bar:<50} {rms:.0f}", end="", flush=True)

                    keyword_index = porcupine.process(pcm)
                    if keyword_index >= 0:
                        print("\n[JARVIS] ✨ Wake word detected!")
                        on_wake_word_callback()
            finally:
                recorder.stop()
                recorder.delete()
        
        except OSError as e:
            print(f"\n[JARVIS] ⚠️ Microphone Error (Index {config.MIC_INDEX}): {e}")
            print("[JARVIS] Retrying in 3 seconds...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n[JARVIS] 🛑 Wake word detection stopped.")
            break
    
    porcupine.delete()
