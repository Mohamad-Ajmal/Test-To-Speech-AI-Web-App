from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from pydub import AudioSegment, effects

from config.settings import HISTORY_FILE, OUTPUT_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_unique_filename(extension: str) -> str:
    safe_extension = extension.lower().replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"tts_{timestamp}_{uuid.uuid4().hex[:8]}.{safe_extension}"


def output_path(filename: str) -> Path:
    return OUTPUT_DIR / filename


def save_wav(audio: np.ndarray, path: Path, sample_rate: int) -> Path:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, sample_rate)
        return path
    except Exception as exc:
        raise RuntimeError(f"Could not save WAV file: {exc}") from exc


def _find_ffmpeg() -> str | None:
    env_path = os.getenv("FFMPEG_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    found = shutil.which("ffmpeg")
    if found:
        return found

    possible_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\Users\Ajmal\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe",
    ]
    for item in possible_paths:
        if Path(item).exists():
            return item
    return None


def polish_wav(input_path: Path, output_path_: Path | None = None, normalize: bool = True) -> Path:
    """Normalize volume and add subtle fade-in/fade-out for a more polished output."""
    try:
        output_path_ = output_path_ or input_path
        audio = AudioSegment.from_wav(str(input_path))
        if normalize:
            audio = effects.normalize(audio)
        audio = audio.fade_in(80).fade_out(140)
        audio.export(str(output_path_), format="wav")
        return output_path_
    except Exception as exc:
        raise RuntimeError(f"Audio polishing failed: {exc}") from exc


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> Path:
    """Convert WAV to MP3. Uses PATH, FFMPEG_PATH, or a known Windows Winget location."""
    try:
        ffmpeg_path = _find_ffmpeg()
        if ffmpeg_path is None:
            raise FileNotFoundError("FFmpeg executable was not found.")

        AudioSegment.converter = ffmpeg_path
        audio = AudioSegment.from_wav(str(wav_path))
        audio.export(str(mp3_path), format="mp3", bitrate="192k")
        return mp3_path
    except FileNotFoundError as exc:
        raise RuntimeError(
            "MP3 export requires FFmpeg. Install FFmpeg and add it to PATH, set FFMPEG_PATH, or choose WAV."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"MP3 conversion failed: {exc}") from exc


def clean_old_outputs(max_age_hours: int = 24) -> None:
    cutoff = time.time() - max_age_hours * 3600
    for file in OUTPUT_DIR.glob("tts_*"):
        if file.is_file() and file.stat().st_mtime < cutoff:
            try:
                file.unlink()
            except OSError:
                pass


def _read_history() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_history(items: list[dict[str, Any]]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def add_history_item(item: dict[str, Any], max_items: int = 50) -> None:
    items = _read_history()
    items.insert(0, item)
    _write_history(items[:max_items])


def list_history() -> list[dict[str, Any]]:
    items = _read_history()
    existing = []
    for item in items:
        filename = item.get("filename")
        if filename and (OUTPUT_DIR / filename).exists():
            existing.append(item)
    if len(existing) != len(items):
        _write_history(existing)
    return existing


def delete_output_file(filename: str) -> bool:
    safe_name = Path(filename).name
    target = OUTPUT_DIR / safe_name
    if not target.exists() or not target.is_file():
        return False
    target.unlink()
    items = [item for item in _read_history() if item.get("filename") != safe_name]
    _write_history(items)
    return True
