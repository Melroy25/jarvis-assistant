"""
JARVIS Desktop Client — Main Entry Point

Usage:
  python main.py              # Full mode: wake word + voice commands
  python main.py --test       # Test mode: one command from keyboard input
  python main.py --no-wake    # Skip wake word, go straight to listening loop

Requirements:
  - Fill in .env (copy from .env.example)
  - Download Vosk model and place in ./vosk-model/
  - Obtain Picovoice access key from https://picovoice.ai
"""

import sys
import threading
import time
import config
import command_handler




def run_full_mode():
    """Start wake word detection loop (blocking)."""
    import wake_word
    if not config.PICOVOICE_ACCESS_KEY:
        print("[JARVIS] ⚠️  No Picovoice access key set in .env. Cannot use wake word.")
        print("[JARVIS] Running in --no-wake mode instead.")
        run_no_wake_mode()
        return

    print("=" * 60)
    print("  JARVIS Desktop Client — Running")
    print("=" * 60)
    print(f"  Backend:   {config.BACKEND_URL}")
    print(f"  Device ID: {config.DEVICE_ID}")
    print(f"  Wake word: 'Jarvis'")
    print("=" * 60)

    import speech
    
    # Pre-optimize: Load brain before starting
    print("[JARVIS] ⚡ Optimizing systems for speed...")
    speech.preload_model()
    
    speech.speak("Master Melroy, I'm ready to serve you.")
    
    def on_activation():
        print("[JARVIS] ✨ Activation! Entering conversation mode...")
        
        # Only say "Yes?" for the very first command
        if not config.FAST_RESPONSE:
            speech.speak("Yes?")

        # Follow-up Loop: Stay active for continuous conversation
        while True:
            command = speech.listen(max_duration=15)
            
            if not command:
                print("[JARVIS] 🌙 No follow-up detected. Returning to idle.")
                break 

            response = command_handler.process_command(command)
            speech.speak(response)
            print("[JARVIS] 👂 Listening for next command...")

    wake_word.start_listening(on_activation)


def run_no_wake_mode():
    """Listen for commands directly without wake word check."""
    import speech
    print("[JARVIS] Running in direct listening mode (no wake word). Press Ctrl+C to stop.")
    speech.speak("Master Melroy, I'm ready to serve you.")
    while True:
        try:
            text = speech.listen()
            if text:
                response = command_handler.process_command(text)
                speech.speak(response)
        except KeyboardInterrupt:
            print("\n[JARVIS] Shutting down.")
            break


def run_test_mode():
    """Accept commands from keyboard and print responses (no mic needed)."""
    print("[JARVIS] Test mode — type commands below. Ctrl+C to quit.")
    while True:
        try:
            text = input("\n> Enter command: ").strip()
            if text:
                response = command_handler.process_command(text)
                print(f"[JARVIS] Response: {response}")
        except (KeyboardInterrupt, EOFError):
            print("\n[JARVIS] Test mode ended.")
            break


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--test" in args:
        run_test_mode()
    elif "--no-wake" in args:
        run_no_wake_mode()
    else:
        run_full_mode()
