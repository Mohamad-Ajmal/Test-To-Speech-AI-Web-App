from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from audio_utils import clean_old_outputs, delete_output_file, list_history
from config.settings import (
    APP_NAME,
    MAX_CHARS,
    MAX_SPEED,
    MIN_SPEED,
    OUTPUT_DIR,
    STYLE_PRESETS,
    SUPPORTED_FORMATS,
    SUPPORTED_VOICES,
)
from tts_engine import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME, version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local development convenience; restrict this before public deployment
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    clean_old_outputs(max_age_hours=24)
    try:
        engine.load()
    except RuntimeError as exc:
        logger.error("Startup warning: %s", exc)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": APP_NAME,
        "model_loaded": engine.pipeline is not None,
        "voices": SUPPORTED_VOICES,
        "style_presets": STYLE_PRESETS,
    }


@app.get("/voices")
def get_voices() -> dict:
    grouped: dict[str, list[dict]] = {}
    for key, item in SUPPORTED_VOICES.items():
        group = item.get("category", "Other Voices")
        grouped.setdefault(group, []).append({"key": key, **item})
    return {"voices": SUPPORTED_VOICES, "grouped": grouped}


@app.get("/presets")
def get_presets() -> dict:
    return {"style_presets": STYLE_PRESETS}


@app.get("/history")
def get_history() -> dict:
    return {"items": list_history()}


@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    media_type = "audio/mpeg" if file_path.suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(path=file_path, media_type=media_type, filename=safe_name)


@app.delete("/history/{filename}")
def delete_history_item(filename: str) -> dict:
    deleted = delete_output_file(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return {"deleted": True, "filename": Path(filename).name}


@app.post("/generate")
def generate(
    text: str = Form(...),
    voice: str = Form("professional_female"),
    speed: float = Form(1.0),
    output_format: str = Form("wav"),
    style_preset: str = Form("business"),
    polish: bool = Form(True),
) -> FileResponse:
    text = (text or "").strip()
    output_format = output_format.lower().strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > MAX_CHARS:
        raise HTTPException(status_code=400, detail=f"Text is too long. Maximum is {MAX_CHARS} characters.")
    if voice not in SUPPORTED_VOICES:
        raise HTTPException(status_code=400, detail="Unsupported voice selected.")
    if style_preset not in STYLE_PRESETS:
        raise HTTPException(status_code=400, detail="Unsupported style preset selected.")
    if output_format not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported format. Choose wav or mp3.")
    if not (MIN_SPEED <= speed <= MAX_SPEED):
        raise HTTPException(status_code=400, detail=f"Speed must be between {MIN_SPEED} and {MAX_SPEED}.")

    try:
        file_path = engine.generate_audio(
            text=text,
            voice_key=voice,
            speed=speed,
            output_format=output_format,
            style_preset=style_preset,
            polish=polish,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Audio generation failed.")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {exc}") from exc

    media_type = "audio/wav" if output_format == "wav" else "audio/mpeg"
    return FileResponse(path=file_path, media_type=media_type, filename=Path(file_path).name)


@app.exception_handler(Exception)
def global_exception_handler(_, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error. Check backend logs."})
