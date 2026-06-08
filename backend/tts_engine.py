"""Kokoro TTS engine wrapper with style presets, voice metadata, and audio polishing."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from threading import Lock
from typing import List

import numpy as np

from audio_utils import (
    add_history_item,
    convert_wav_to_mp3,
    create_unique_filename,
    output_path,
    polish_wav,
    save_wav,
)
from config.settings import SAMPLE_RATE, STYLE_PRESETS, SUPPORTED_VOICES
from text_cleaner import split_text_into_chunks

logger = logging.getLogger(__name__)
PAUSE_PATTERN = re.compile(r"\[pause:(\d+)(ms|s)\]", flags=re.IGNORECASE)


class KokoroTTSEngine:
    def __init__(self, default_lang_code: str = "a") -> None:
        self.default_lang_code = default_lang_code
        self.pipelines: dict[str, object] = {}
        self.pipeline = None  # kept for older /health compatibility
        self._lock = Lock()

    def load(self) -> None:
        """Load the default Kokoro pipeline once during startup."""
        self._get_pipeline(self.default_lang_code)

    def _get_pipeline(self, lang_code: str):
        if lang_code in self.pipelines:
            return self.pipelines[lang_code]
        try:
            from kokoro import KPipeline

            # repo_id suppresses Kokoro's default repo warning on newer versions.
            try:
                pipeline = KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M")
            except TypeError:
                pipeline = KPipeline(lang_code=lang_code)

            self.pipelines[lang_code] = pipeline
            if self.pipeline is None:
                self.pipeline = pipeline
            logger.info("Kokoro TTS pipeline loaded successfully for lang_code=%s.", lang_code)
            return pipeline
        except Exception as exc:
            logger.exception("Failed to load Kokoro TTS.")
            raise RuntimeError(
                "Could not load Kokoro TTS. Check that kokoro, soundfile, and espeak-ng are installed. "
                f"Original error: {exc}"
            ) from exc

    def _resolve_voice(self, voice_key: str) -> dict:
        if voice_key in SUPPORTED_VOICES:
            return SUPPORTED_VOICES[voice_key]
        supported = ", ".join(SUPPORTED_VOICES.keys())
        raise ValueError(f"Unsupported voice '{voice_key}'. Supported voices: {supported}")

    def _generate_segment(self, text: str, kokoro_voice: str, lang_code: str, speed: float) -> np.ndarray:
        pipeline = self._get_pipeline(lang_code)

        try:
            generator = pipeline(text, voice=kokoro_voice, speed=speed)
        except TypeError:
            generator = pipeline(text, voice=kokoro_voice)

        pieces: List[np.ndarray] = []
        for _, _, audio in generator:
            pieces.append(np.asarray(audio, dtype=np.float32))

        if not pieces:
            raise RuntimeError("Kokoro returned no audio for the provided text.")
        return np.concatenate(pieces)

    def _pause_audio(self, pause_ms: int) -> np.ndarray:
        pause_ms = max(50, min(int(pause_ms), 5000))
        return np.zeros(int(SAMPLE_RATE * pause_ms / 1000), dtype=np.float32)

    def _append_text_with_pause_markers(
        self,
        audio_parts: list[np.ndarray],
        text: str,
        kokoro_voice: str,
        lang_code: str,
        speed: float,
    ) -> None:
        cursor = 0
        for match in PAUSE_PATTERN.finditer(text):
            before = text[cursor : match.start()].strip()
            if before:
                audio_parts.append(self._generate_segment(before, kokoro_voice, lang_code, speed))
            amount = int(match.group(1))
            unit = match.group(2).lower()
            pause_ms = amount * 1000 if unit == "s" else amount
            audio_parts.append(self._pause_audio(pause_ms))
            cursor = match.end()

        remaining = text[cursor:].strip()
        if remaining:
            audio_parts.append(self._generate_segment(remaining, kokoro_voice, lang_code, speed))

    def generate_audio(
        self,
        text: str,
        voice_key: str,
        speed: float = 1.0,
        output_format: str = "wav",
        style_preset: str = "business",
        polish: bool = True,
    ) -> Path:
        chunks = split_text_into_chunks(text)
        if not chunks:
            raise ValueError("Please enter text before generating audio.")

        voice_data = self._resolve_voice(voice_key)
        kokoro_voice = voice_data["kokoro_voice"]
        lang_code = voice_data.get("lang_code", self.default_lang_code)

        output_format = output_format.lower()
        if output_format not in {"wav", "mp3"}:
            raise ValueError("Unsupported output format. Choose WAV or MP3.")

        preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["business"])
        final_speed = max(0.7, min(1.35, float(speed) * float(preset.get("speed_multiplier", 1.0))))
        pause_ms = int(preset.get("pause_ms", 350))
        should_normalize = bool(preset.get("normalize", True)) and polish

        all_audio: list[np.ndarray] = []

        with self._lock:
            for index, chunk in enumerate(chunks, start=1):
                logger.info("Generating chunk %s/%s with voice=%s style=%s", index, len(chunks), voice_key, style_preset)
                self._append_text_with_pause_markers(all_audio, chunk, kokoro_voice, lang_code, final_speed)
                if index < len(chunks):
                    all_audio.append(self._pause_audio(pause_ms))

        if not all_audio:
            raise RuntimeError("No audio was generated.")

        final_audio = np.concatenate(all_audio).astype(np.float32)
        wav_name = create_unique_filename("wav")
        wav_path = output_path(wav_name)
        save_wav(final_audio, wav_path, SAMPLE_RATE)

        if polish:
            polish_wav(wav_path, wav_path, normalize=should_normalize)

        result_path = wav_path
        if output_format == "mp3":
            mp3_path = output_path(wav_path.stem + ".mp3")
            result_path = convert_wav_to_mp3(wav_path, mp3_path)

        add_history_item(
            {
                "filename": result_path.name,
                "format": output_format,
                "voice_key": voice_key,
                "voice_label": voice_data.get("label", voice_key),
                "style_preset": style_preset,
                "style_label": preset.get("label", style_preset),
                "speed": speed,
                "effective_speed": round(final_speed, 3),
                "sample_rate": SAMPLE_RATE,
                "text_preview": text.strip().replace("\n", " ")[:180],
            }
        )

        return result_path


engine = KokoroTTSEngine()
