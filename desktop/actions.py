"""
JARVIS Desktop Actions
Handles executing local system commands based on parsed intents.
"""
import os
import sys
import subprocess
import webbrowser
import datetime
import platform
import requests
import config

# ─── App Launcher ──────────────────────────────────────────────────────────────

# Map of common app names to their executables (Windows-focused)
APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "notepad": "notepad",
    "calculator": "calc",
    "excel": "excel",
    "word": "winword",
    "powerpoint": "powerpnt",
    "spotify": "Spotify",
    "vlc": "vlc",
    "vs code": "code",
    "visual studio code": "code",
    "terminal": "cmd",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "paint": "mspaint",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
}


def open_app(app_name: str) -> str:
    """Try to open an application by name."""
    name = app_name.lower().strip()
    executable = APP_MAP.get(name, name)

    try:
        if platform.system() == "Windows":
            subprocess.Popen(["start", executable], shell=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen([executable])
        return f"Opening {app_name}."
    except FileNotFoundError:
        return f"Sorry, I couldn't find the application '{app_name}'."
    except Exception as e:
        return f"Failed to open {app_name}: {e}"


def open_website(url: str) -> str:
    """Open a URL in the default web browser."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url} in your browser."


# ─── Alarm / Reminder ─────────────────────────────────────────────────────────

def set_reminder(time_str: str, message: str = "JARVIS Reminder") -> str:
    """
    Sets a desktop notification reminder using a background thread.
    time_str can be like "07:00 AM", "in 5 minutes", etc.
    """
    import threading
    import time

    def _parse_seconds(t: str) -> int | None:
        """Parse time string to seconds from now."""
        t = t.strip().lower()
        if "minute" in t:
            mins = int("".join(filter(str.isdigit, t)) or "5")
            return mins * 60
        if "second" in t:
            secs = int("".join(filter(str.isdigit, t)) or "30")
            return secs
        if "hour" in t:
            hours = int("".join(filter(str.isdigit, t)) or "1")
            return hours * 3600
        # Try parsing an absolute time like "07:00 AM"
        try:
            now = datetime.datetime.now()
            target = datetime.datetime.strptime(t.upper(), "%I:%M %p").replace(
                year=now.year, month=now.month, day=now.day
            )
            if target < now:
                target += datetime.timedelta(days=1)
            return int((target - now).total_seconds())
        except ValueError:
            return None

    from plyer import notification

    seconds = _parse_seconds(time_str)
    if seconds is None:
        return f"I couldn't understand the time '{time_str}'. Please say something like 'in 5 minutes' or '7:00 AM'."

    def _fire():
        time.sleep(seconds)
        notification.notify(
            title="⏰ JARVIS Reminder",
            message=message,
            app_name="JARVIS",
            timeout=10,
        )
        print(f"[JARVIS] 🔔 Reminder fired: {message}")

    t = threading.Thread(target=_fire, daemon=True)
    t.start()
    return f"Reminder set for {time_str}. I'll notify you."


def set_alarm(time_str: str) -> str:
    """Alias for set_reminder specifically for alarms."""
    return set_reminder(time_str, message=f"⏰ Alarm: {time_str}")


# ─── Weather ──────────────────────────────────────────────────────────────────

def get_weather(city: str) -> str:
    """Fetch weather from JARVIS backend."""
    try:
        res = requests.get(
            f"{config.BACKEND_URL}/api/weather",
            params={"city": city},
            headers={"Authorization": f"Bearer {config.API_TOKEN}"},
            timeout=10,
        )
        data = res.json()
        if data.get("success"):
            return data["weather"]["response_text"]
        return f"Couldn't get weather for {city}: {data.get('message', 'Unknown error')}"
    except requests.RequestException as e:
        return f"Weather request failed: {e}"


# ─── System Info ──────────────────────────────────────────────────────────────

def get_time() -> str:
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def get_date() -> str:
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."


# ─── Automation (PyAutoGUI) ──────────────────────────────────────────────────

def type_text(text: str) -> str:
    """Type the given text exactly into the active window."""
    try:
        import pyautogui
        import time
        # Slight delay to ensure focus
        time.sleep(0.5)
        pyautogui.write(text, interval=0.02)
        return "I've typed that out for you, sir."
    except Exception as e:
        return f"Failed to type: {e}"


def press_key(key: str) -> str:
    """Press a specific key (e.g., 'enter', 'tab', 'shift')."""
    try:
        import pyautogui
        pyautogui.press(key.lower())
        return f"Pressed '{key}'."
    except Exception as e:
        return f"Failed to press key: {e}"


def hotkey(*args) -> str:
    """Press a combination of keys (e.g., 'ctrl', 's')."""
    try:
        import pyautogui
        pyautogui.hotkey(*args)
        return f"Hotket combination {args} executed."
    except Exception as e:
        return f"Failed to execute hotkey: {e}"


def volume_control(level: int) -> str:
    """Set system volume level (0-100)."""
    try:
        if platform.system() == "Windows":
            # Convert 0-100 to 0-65535 for NirCmd or similar, 
            # but PowerShell is built-in
            # (65536 / 100) * level
            v = int(level)
            cmd = f"$w = New-Object -ComObject WScript.Shell; for($i=0; $i -lt 50; $i++) {{ $w.SendKeys([char]174) }}; for($i=0; $i -lt {v/2}; $i++) {{ $w.SendKeys([char]175) }}"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            return f"Volume set to {level} percent."
        return "Volume control is only supported on Windows for now."
    except Exception as e:
        return f"Failed to set volume: {e}"


def take_screenshot() -> str:
    """Capture the screen and save it to the Pictures folder."""
    try:
        from PIL import ImageGrab
        import datetime
        
        # Determine saving path (Pictures folder)
        home = os.path.expanduser("~")
        pictures_path = os.path.join(home, "Pictures", "JARVIS_Screenshots")
        if not os.path.exists(pictures_path):
            os.makedirs(pictures_path)
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Screenshot_{timestamp}.png"
        file_path = os.path.join(pictures_path, filename)
        
        # Capture and save
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)
        
        return f"Screenshot saved successfully to your Pictures folder as {filename}, sir."
    except Exception as e:
        return f"Failed to take screenshot: {e}"


