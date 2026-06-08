# AI Text-to-Audio Generator

A complete local Text-to-Speech web application that lets you paste a script, choose a professional voice, adjust speed, and generate downloadable audio.

The project uses:

- Python FastAPI backend
- Kokoro TTS as the main CPU-friendly TTS engine
- React + Vite frontend
- Tailwind CSS custom landing page
- WAV output by default
- Optional MP3 conversion through pydub and FFmpeg

---

## 1. Project overview

AI Text-to-Audio Generator is designed for local voiceover generation on a laptop without a paid cloud API. It is suitable for:

- YouTube narration
- Training videos
- Presentation voiceovers
- Announcements
- Business content
- Educational scripts

The backend cleans and splits long text, sends each chunk to Kokoro TTS, combines the generated audio, saves it locally, and returns the final audio file to the React frontend.

---

## 2. System requirements

Recommended system:

- CPU: Intel Core i7 13th Gen or similar
- RAM: 16 GB minimum, 64 GB recommended for long scripts
- Storage: 10 GB free minimum; 1 TB is more than enough
- GPU: Not required
- Python: 3.10 or 3.11 recommended
- Node.js: 18 or newer
- Browser: Chrome, Edge, Firefox, or Brave

Your Dell Latitude 7440 with 64 GB RAM and Intel Core i7 13th Gen is suitable for this CPU-based project.

---

## 3. Backend setup

Open a terminal in the project folder:

```bash
cd ai_text_to_audio/backend
python -m venv venv
```

Activate the virtual environment.

Windows PowerShell or CMD:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Important: install espeak-ng

Kokoro uses `espeak-ng` for English fallback and some language/phoneme support.

Windows:

1. Download and install eSpeak NG from its official releases page.
2. Add the installation folder to your system PATH if needed.
3. Restart the terminal.

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install espeak-ng
```

macOS:

```bash
brew install espeak-ng
```

---

## 4. Run backend

From `ai_text_to_audio/backend`:

```bash
uvicorn app:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## 5. Frontend setup

Open a second terminal:

```bash
cd ai_text_to_audio/frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

---

## 6. How to use

1. Start the backend first.
2. Start the frontend second.
3. Open `http://127.0.0.1:5173` in your browser.
4. Paste your script.
5. Select a voice.
6. Adjust speed.
7. Choose WAV or MP3.
8. Click **Generate Audio**.
9. Preview the generated audio.
10. Download the file.

Generated files are saved in:

```text
backend/outputs/
```

---

## 7. Voice options

The frontend labels are mapped to Kokoro voices in `backend/config/settings.py`.

| Frontend label | Backend key | Kokoro voice |
|---|---|---|
| Professional Female Voice | professional_female | af_heart |
| Professional Male Voice | professional_male | am_adam |
| Soft Female Voice | soft_female | af_bella |
| Deep Male Voice | deep_male | am_michael |

To add more voices later, edit `SUPPORTED_VOICES` in:

```text
backend/config/settings.py
```

Then add the matching option to:

```text
frontend/src/components/TextToAudioForm.jsx
```

---

## 8. How the project works

### Backend flow

1. React sends `text`, `voice`, `speed`, and `output_format` to `POST /generate`.
2. FastAPI validates the request.
3. `text_cleaner.py` cleans punctuation, spaces, and symbols.
4. The script is split into smaller chunks for safer local CPU generation.
5. `tts_engine.py` sends chunks to Kokoro TTS.
6. Audio chunks are combined with small pauses.
7. `audio_utils.py` saves a WAV file.
8. If MP3 is selected, pydub uses FFmpeg to convert the WAV to MP3.
9. The backend returns the audio file as a downloadable response.

### Frontend flow

1. User enters a script in the landing page generator.
2. Axios sends a `FormData` request to FastAPI.
3. The response audio blob is converted into a browser preview URL.
4. The audio player and download button appear.

---

## 9. Troubleshooting

### Backend offline

Error:

```text
Backend is offline. Start FastAPI at http://127.0.0.1:8000 and try again.
```

Fix:

```bash
cd backend
venv\Scripts\activate
uvicorn app:app --reload
```

### Kokoro cannot load

Possible causes:

- `kokoro` package is not installed
- `espeak-ng` is missing
- Python version is incompatible

Fix:

```bash
pip install -r requirements.txt
```

Then install `espeak-ng` for your operating system.

### MP3 export fails

MP3 export requires FFmpeg. If FFmpeg is not installed, choose WAV or install FFmpeg.

Windows:

1. Download FFmpeg.
2. Add `ffmpeg/bin` to PATH.
3. Restart terminal.

Ubuntu/Debian:

```bash
sudo apt-get install ffmpeg
```

macOS:

```bash
brew install ffmpeg
```

### Generation is slow

This is normal on CPU for long scripts. Tips:

- Use WAV instead of MP3 for faster export.
- Start with shorter scripts for testing.
- Close heavy applications while generating.
- Keep speed near `1.0` for natural output.

### Unsupported voice

Make sure the selected voice key exists in `SUPPORTED_VOICES`.

### Empty text

The backend rejects empty scripts. Enter text before generating audio.

---

## 10. Future upgrade ideas

The current architecture is ready for later upgrades:

- Add XTTS-v2 for voice cloning
- Add Piper TTS engine for very fast local voices
- Add multiple languages
- Add user accounts
- Add audio history
- Add batch script-to-audio conversion
- Add background queue processing
- Add Docker deployment
- Add waveform visualization
- Add subtitle/script timing export

A future engine abstraction could look like this:

```text
backend/engines/
├── base.py
├── kokoro_engine.py
├── piper_engine.py
└── xtts_engine.py
```

---

## 11. Ethical notes about voice cloning

This project currently uses preset TTS voices, not voice cloning. If you add XTTS-v2 or another cloning engine later:

- Only clone voices with clear permission.
- Do not impersonate real people.
- Do not create misleading political, financial, or personal content.
- Label synthetic audio where appropriate.
- Follow local law and platform rules.

---

## 12. File structure

```text
ai_text_to_audio/
│
├── backend/
│   ├── app.py
│   ├── tts_engine.py
│   ├── text_cleaner.py
│   ├── audio_utils.py
│   ├── requirements.txt
│   ├── outputs/
│   └── config/
│       └── settings.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/
│       │   └── ttsApi.js
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── Hero.jsx
│       │   ├── TextToAudioForm.jsx
│       │   ├── AudioPreview.jsx
│       │   ├── Features.jsx
│       │   ├── HowItWorks.jsx
│       │   └── Footer.jsx
│       └── assets/
│
└── README.md
```
