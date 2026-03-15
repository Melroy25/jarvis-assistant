"""
JARVIS Command Handler
Sends text to backend, parses response, and dispatches to local actions.
"""
import requests
import actions
import config


def process_command(text: str) -> str:
    """Sends text to backend, gets a sequence of actions, and executes them."""
    if not text:
        return "I didn't catch that. Could you repeat?"

    try:
        response = requests.post(
            f"{config.BACKEND_URL}/api/command",
            json={"text": text, "deviceId": config.DEVICE_ID},
            headers={
                "Authorization": f"Bearer {config.API_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

    actions_list = data.get("actions", [])
    response_text = data.get("response_text", "Done.")

    if not actions_list:
        # Fallback for old single-intent format if any
        intent = data.get("intent")
        params = data.get("parameters", {})
        if intent:
            _dispatch(intent, params)
        else:
            import time
            for action in actions_list:
                intent = action.get("intent")
                params = action.get("parameters", {})
                if intent:
                    # Small grace period before execution
                    time.sleep(0.3)
                    print(f"[JARVIS] ⚙️ Executing: {intent}...")
                    _dispatch(intent, params)
                    
                    # Longer delay for hotkeys (like opening 'Save As' dialog)
                    if intent == "hotkey":
                        time.sleep(1.8)
                    else:
                        time.sleep(1.0)

    return response_text


def _dispatch(intent: str, params: dict) -> str | None:
    """Route intent to a local action handler."""

    if intent == "alarm":
        time_str = params.get("time", "unknown time")
        return actions.set_alarm(time_str)

    elif intent == "reminder":
        time_str = params.get("time", "in 5 minutes")
        message = params.get("message", "JARVIS Reminder")
        return actions.set_reminder(time_str, message)

    elif intent == "weather":
        city = params.get("city", "London")
        return actions.get_weather(city)

    elif intent == "open_app":
        app = params.get("app", "")
        url = params.get("url", "")
        if url:
            return actions.open_website(url)
        elif app:
            return actions.open_app(app)

    elif intent == "screenshot":
        return actions.take_screenshot()

    elif intent == "type_text":
        text_to_type = params.get("text", "")
        return actions.type_text(text_to_type)

    elif intent == "press_key":
        key = params.get("key", "enter")
        return actions.press_key(key)

    elif intent == "hotkey":
        keys = params.get("keys", [])
        if isinstance(keys, str):
            keys = [keys]
        return actions.hotkey(*keys)

    elif intent == "volume_control":
        level = params.get("level", 50)
        return actions.volume_control(level)

    elif intent == "general":
        # Pure conversational — just read the backend response
        return None

    elif intent in ("call", "sms"):
        # Not supported on desktop
        return "Calling and SMS are only supported on the mobile app."

    return None
