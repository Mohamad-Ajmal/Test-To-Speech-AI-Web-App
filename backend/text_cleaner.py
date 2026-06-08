from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from config.settings import PRONUNCIATION_FILE

_SYMBOL_REPLACEMENTS = {
    "%": " percent ",
    "$": " dollars ",
    "€": " euros ",
    "£": " pounds ",
    "&": " and ",
    "@": " at ",
    "+": " plus ",
    "=": " equals ",
}

_ABBREVIATIONS = {
    "Dr.": "Doctor",
    "Mr.": "Mister",
    "Mrs.": "Misses",
    "Ms.": "Miss",
    "Prof.": "Professor",
    "St.": "Saint",
    "e.g.": "for example",
    "i.e.": "that is",
    "etc.": "et cetera",
}


def load_pronunciation_dictionary() -> dict[str, str]:
    if not PRONUNCIATION_FILE.exists():
        return {}
    try:
        data = json.loads(PRONUNCIATION_FILE.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in data.items()}
    except Exception:
        return {}


def apply_pronunciation_dictionary(text: str) -> str:
    dictionary = load_pronunciation_dictionary()
    for word, pronunciation in dictionary.items():
        text = re.sub(rf"\b{re.escape(word)}\b", pronunciation, text)
    return text


def normalize_numbers_and_units(text: str) -> str:
    text = re.sub(r"\b(\d+)\s*%", r"\1 percent", text)
    text = re.sub(r"\$\s*(\d+(?:\.\d+)?)", r"\1 dollars", text)
    text = re.sub(r"\b(\d+)\s*km\b", r"\1 kilometers", text, flags=re.I)
    text = re.sub(r"\b(\d+)\s*kg\b", r"\1 kilograms", text, flags=re.I)
    text = re.sub(r"\b(\d+)\s*GB\b", r"\1 gigabytes", text, flags=re.I)
    text = re.sub(r"\b(\d+)\s*MB\b", r"\1 megabytes", text, flags=re.I)
    return text


def normalize_bullets_and_headings(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("[pause:700ms]")
            continue
        line = re.sub(r"^[-*•]+\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if line.endswith(":") and len(line.split()) <= 8:
            line = line[:-1] + ". [pause:500ms]"
        lines.append(line)
    return " ".join(lines)


def clean_text(text: str) -> str:
    text = text.strip()
    text = normalize_bullets_and_headings(text)
    text = apply_pronunciation_dictionary(text)

    for old, new in _ABBREVIATIONS.items():
        text = text.replace(old, new)

    text = normalize_numbers_and_units(text)

    for symbol, word in _SYMBOL_REPLACEMENTS.items():
        text = text.replace(symbol, word)

    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;!?])", r"\1", text)
    text = re.sub(r"([,.;!?])(?=\S)", r"\1 ", text)
    text = re.sub(r"([!?.,]){2,}", r"\1", text)
    text = text.strip()

    if text and text[-1] not in ".!?]":
        text += "."
    return text


def split_text_into_chunks(text: str, max_chars: int = 650) -> list[str]:
    cleaned = clean_text(text)
    if len(cleaned) <= max_chars:
        return [cleaned]

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_sentence(sentence, max_chars))
            continue

        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())
    return chunks


def _split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    parts = re.split(r"(?<=[,;:])\s+", sentence)
    chunks = []
    current = ""
    for part in parts:
        candidate = f"{current} {part}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = part
    if current:
        chunks.append(current.strip())
    return chunks
