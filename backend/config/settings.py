from __future__ import annotations

from pathlib import Path

APP_NAME = "AI Text-to-Audio Generator"
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
PRONUNCIATION_FILE = BASE_DIR / "config" / "pronunciation.json"
HISTORY_FILE = OUTPUT_DIR / "history.json"

SAMPLE_RATE = 24000
MAX_CHARS = 30000
MIN_SPEED = 0.7
MAX_SPEED = 1.35
SUPPORTED_FORMATS = {"wav", "mp3"}

STYLE_PRESETS = {
    "business": {
        "label": "Business Presentation",
        "speed_multiplier": 0.95,
        "pause_ms": 420,
        "normalize": True,
        "description": "Clear, polished narration for meetings, reports, and presentations.",
    },
    "youtube": {
        "label": "YouTube Voiceover",
        "speed_multiplier": 1.04,
        "pause_ms": 300,
        "normalize": True,
        "description": "Engaging pacing for videos, explainers, and social content.",
    },
    "training": {
        "label": "Training Course",
        "speed_multiplier": 0.9,
        "pause_ms": 560,
        "normalize": True,
        "description": "Slower, clearer delivery for lessons and tutorials.",
    },
    "announcement": {
        "label": "Announcement",
        "speed_multiplier": 0.92,
        "pause_ms": 650,
        "normalize": True,
        "description": "Formal pacing for public announcements and notices.",
    },
    "storytelling": {
        "label": "Calm Storytelling",
        "speed_multiplier": 0.88,
        "pause_ms": 700,
        "normalize": True,
        "description": "Relaxed narration for stories, meditation, and reflective scripts.",
    },
    "promo": {
        "label": "Energetic Promo",
        "speed_multiplier": 1.08,
        "pause_ms": 250,
        "normalize": True,
        "description": "Faster and more energetic style for marketing and promos.",
    },
}

SUPPORTED_VOICES = {
    "professional_female": {
        "label": "Professional Female Voice",
        "kokoro_voice": "af_heart",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Clear, warm, professional American female voice.",
    },
    "professional_male": {
        "label": "Professional Male Voice",
        "kokoro_voice": "am_adam",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Balanced American male voice for business narration.",
    },
    "soft_female": {
        "label": "Soft Female Voice",
        "kokoro_voice": "af_bella",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Soft, friendly female voice for calm content.",
    },
    "deep_male": {
        "label": "Deep Male Voice",
        "kokoro_voice": "am_michael",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Deeper male voice for announcements and explainers.",
    },
    "calm_female": {
        "label": "Calm Female Voice",
        "kokoro_voice": "af_nicole",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Calm, articulate female voice for training and narration.",
    },
    "modern_female": {
        "label": "Modern Female Voice",
        "kokoro_voice": "af_nova",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Modern and dynamic American female voice.",
    },
    "bright_female": {
        "label": "Bright Female Voice",
        "kokoro_voice": "af_kore",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Bright and energetic American female voice.",
    },
    "light_female": {
        "label": "Light Female Voice",
        "kokoro_voice": "af_sky",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Light and clean female voice for soft narration.",
    },
    "casual_female": {
        "label": "Casual Female Voice",
        "kokoro_voice": "af_sarah",
        "lang_code": "a",
        "accent": "American",
        "gender": "Female",
        "category": "American Female Voices",
        "description": "Casual and approachable American female voice.",
    },
    "authoritative_male": {
        "label": "Authoritative Male Voice",
        "kokoro_voice": "am_eric",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Professional and authoritative American male voice.",
    },
    "rich_male": {
        "label": "Rich Male Voice",
        "kokoro_voice": "am_onyx",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Rich and sophisticated American male voice.",
    },
    "energetic_male": {
        "label": "Energetic Male Voice",
        "kokoro_voice": "am_puck",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Playful and energetic male voice.",
    },
    "clear_male": {
        "label": "Clear Male Voice",
        "kokoro_voice": "am_echo",
        "lang_code": "a",
        "accent": "American",
        "gender": "Male",
        "category": "American Male Voices",
        "description": "Clear and resonant American male voice.",
    },
    "british_female": {
        "label": "British Female Voice",
        "kokoro_voice": "bf_emma",
        "lang_code": "b",
        "accent": "British",
        "gender": "Female",
        "category": "British Female Voices",
        "description": "Warm and professional British female voice.",
    },
    "elegant_british_female": {
        "label": "Elegant British Female Voice",
        "kokoro_voice": "bf_isabella",
        "lang_code": "b",
        "accent": "British",
        "gender": "Female",
        "category": "British Female Voices",
        "description": "Elegant British female voice for premium narration.",
    },
    "soft_british_female": {
        "label": "Soft British Female Voice",
        "kokoro_voice": "bf_lily",
        "lang_code": "b",
        "accent": "British",
        "gender": "Female",
        "category": "British Female Voices",
        "description": "Soft British female voice for storytelling.",
    },
    "british_male": {
        "label": "British Male Voice",
        "kokoro_voice": "bm_george",
        "lang_code": "b",
        "accent": "British",
        "gender": "Male",
        "category": "British Male Voices",
        "description": "Classic British male accent.",
    },
    "polished_british_male": {
        "label": "Polished British Male Voice",
        "kokoro_voice": "bm_daniel",
        "lang_code": "b",
        "accent": "British",
        "gender": "Male",
        "category": "British Male Voices",
        "description": "Polished British male voice for professional content.",
    },
    "story_british_male": {
        "label": "Storytelling British Male Voice",
        "kokoro_voice": "bm_fable",
        "lang_code": "b",
        "accent": "British",
        "gender": "Male",
        "category": "British Male Voices",
        "description": "Storytelling-style British male voice.",
    },
}
