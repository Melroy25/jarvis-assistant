# JARVIS – Cross-Device AI Assistant

> Privacy-focused AI assistant with anime-style UI, wake word activation ("Jarvis"), and cross-device support across Android and laptop.

## Project Structure

```
jarvis-assistant/
├── backend/       ← Next.js API (deploy to Vercel)
├── desktop/       ← Python automation client (Windows/macOS/Linux)
└── mobile/        ← Android app (Kotlin)
```

---

## 1. Backend Setup (Next.js / Vercel)

```bash
cd backend
cp .env.example .env
# Fill in .env with your API keys
npm install
npm run dev
```

**Environment Variables (`.env`):**
| Variable | Description |
|---|---|
| `GROQ_API_KEY` | From https://console.groq.com |
| `WEATHER_API_KEY` | From https://openweathermap.org/api |
| `JARVIS_API_TOKEN` | Any random secret shared between devices |

**API Endpoints:**
| Endpoint | Method | Description |
|---|---|---|
| `/api/command` | POST | Process voice command, returns intent + response |
| `/api/weather` | GET | Weather for `?city=London` |
| `/api/auth` | GET | Ping / token validation |

**Deploy to Vercel:**
```bash
npx vercel --prod
# Set env vars in Vercel dashboard → Settings → Environment Variables
```

---

## 2. Desktop Client Setup (Python)

### Prerequisites
- Python 3.10+
- [Vosk model](https://alphacephei.com/vosk/models) — download `vosk-model-small-en-us-0.15`, extract to `desktop/vosk-model/`
- [Picovoice access key](https://picovoice.ai) — free account

```bash
cd desktop
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set BACKEND_URL, JARVIS_API_TOKEN, PICOVOICE_ACCESS_KEY
```

**Run Modes:**
```bash
python main.py            # Full mode: say "Jarvis" to activate
python main.py --no-wake  # Skip wake word, goes straight to mic
python main.py --test     # Type commands via keyboard (no mic needed)
```

---

## 3. Android App Setup (Kotlin)

### Prerequisites
- Android Studio (Hedgehog or newer)
- Android SDK API 26+ (Oreo)
- [Picovoice access key](https://picovoice.ai)

```bash
cd mobile
cp local.properties.example local.properties
# Edit local.properties: set BACKEND_URL, JARVIS_API_TOKEN, PICOVOICE_ACCESS_KEY
```

Open `mobile/` in Android Studio → Run on device or emulator.

### Key Features
| Feature | Implementation |
|---|---|
| Wake word "Jarvis" | Picovoice Porcupine (`WakeWordService.kt`) |
| Voice input | Android `SpeechRecognizer` |
| Voice output | Android `TextToSpeech` |
| Activation animation | Lottie fog + custom `WaveformView` |
| Set alarms | Android `AlarmManager` |
| Call contacts | `Intent.ACTION_CALL` |
| Send SMS | `SmsManager` |
| Open apps | `PackageManager.getLaunchIntentForPackage` |
| AI responses | JARVIS backend `/api/command` |

---

## Security

- All device↔backend communication uses **HTTPS + Bearer token auth**
- Wake word runs **100% locally** — no audio sent to cloud before activation
- No audio is stored or logged
- Token can be rotated by updating `JARVIS_API_TOKEN` in `.env` and `local.properties`

---

## Minimum Working Version Checklist

- [x] Wake word detection ("Jarvis")
- [x] Activation animation (fog + waveform)
- [x] Voice command recognition
- [x] Set alarm
- [x] Weather query
- [x] Open applications
- [x] AI question answering
- [x] Call contacts (Android)
- [x] Send SMS (Android)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Next.js 15, Groq (Llama 3.3 70B) |
| Desktop | Python, pvporcupine, Vosk, pyttsx3 |
| Android | Kotlin, Porcupine Android, Lottie, OkHttp |
| Hosting | Vercel |
| Wake Word | Picovoice Porcupine |
| Weather | OpenWeatherMap API |
