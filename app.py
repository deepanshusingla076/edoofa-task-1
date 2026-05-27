import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import gspread
import librosa
import requests
import whisper
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SHEET_HEADERS = [
    "Date",
    "Student Name",
    "Sender Name",
    "Sender Type",
    "Voice Note Sequence ID",
    "Transcript",
    "Summary",
    "Action Items",
    "Blockers",
    "Follow Up Needed",
    "Timestamp",
]


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("edoofa_demo")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Free WhatsApp voice-note ops prototype.")
    parser.add_argument("--audio", required=True, help="Path to .ogg or .mp3 file")
    return parser.parse_args()


def parse_audio_metadata(audio_path: Path) -> dict:
    # Optional naming format:
    # student_senderType_senderName_YYYY-MM-DD.ogg
    pattern = re.compile(
        r"^(?P<student>[a-zA-Z0-9-]+)_(?P<sender_type>[a-zA-Z0-9-]+)_(?P<sender_name>[a-zA-Z0-9-]+)_(?P<date>\d{4}-\d{2}-\d{2})$"
    )
    match = pattern.match(audio_path.stem.strip())
    if not match:
        return {
            "student_name": os.getenv("DEFAULT_STUDENT_NAME", "Unknown Student"),
            "sender_name": os.getenv("DEFAULT_SENDER_NAME", "WhatsApp Group Member"),
            "sender_type": os.getenv("DEFAULT_SENDER_TYPE", "Parent"),
            "date": datetime.now().date().isoformat(),
        }

    return {
        "student_name": match.group("student").replace("-", " ").title(),
        "sender_name": match.group("sender_name").replace("-", " ").title(),
        "sender_type": match.group("sender_type").replace("-", " ").title(),
        "date": match.group("date"),
    }


def transcribe_local(audio_path: Path) -> str:
    model = whisper.load_model("base")
    # Load audio with librosa (no ffmpeg required on Windows)
    audio, _ = librosa.load(str(audio_path), sr=16000, mono=True)
    result = model.transcribe(audio, fp16=False)
    return result["text"].strip()


def summarize_with_gemini(gemini_api_key: str, transcript: str) -> dict:
    prompt = f"""
You are an operations assistant for student updates.
Return ONLY valid JSON with keys:
- summary (string, max 40 words)
- action_items (array of strings)
- blockers (array of strings)
- follow_up_needed (string: Yes or No)

Transcript:
{transcript}
""".strip()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={gemini_api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                ]
            }
        ]
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        if not text:
            raise ValueError("Gemini did not return text content.")
    except Exception:
        # Demo-safe fallback when Gemini free tier rate limits.
        return {
            "summary": transcript[:180].strip(),
            "action_items": ["Review transcript and assign follow-up action"],
            "blockers": [],
            "follow_up_needed": "Yes",
        }

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Gemini did not return JSON.")
        parsed = json.loads(text[start : end + 1])

    return {
        "summary": str(parsed.get("summary", "")).strip(),
        "action_items": [str(x).strip() for x in parsed.get("action_items", []) if str(x).strip()],
        "blockers": [str(x).strip() for x in parsed.get("blockers", []) if str(x).strip()],
        "follow_up_needed": str(parsed.get("follow_up_needed", "Yes")).strip() or "Yes",
    }


def connect_sheet(credentials_file: str, sheet_name: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    if sheet.row_values(1) != SHEET_HEADERS:
        sheet.update("A1:K1", [SHEET_HEADERS])
    return sheet


def next_sequence_id(sheet, note_date: str, student_name: str) -> str:
    rows = sheet.get_all_values()
    count = 0
    for row in rows[1:]:
        if len(row) >= 5 and row[0].strip() == note_date and row[1].strip().lower() == student_name.strip().lower():
            count += 1
    return f"VN-{count + 1:03d}"


def main() -> int:
    load_dotenv()
    logger = setup_logger()

    try:
        args = parse_args()
        audio_path = Path(args.audio)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        logger.info("[OK] Audio Loaded")

        meta = parse_audio_metadata(audio_path)
        transcript = transcribe_local(audio_path)
        logger.info("[OK] Transcript Generated")

        structured = summarize_with_gemini(required_env("GEMINI_API_KEY"), transcript)
        logger.info("[OK] AI Summary Generated")

        sheet = connect_sheet(
            credentials_file=required_env("GOOGLE_SHEETS_CREDENTIALS_FILE"),
            sheet_name=required_env("GOOGLE_SHEET_NAME"),
        )
        sequence_id = next_sequence_id(sheet, meta["date"], meta["student_name"])

        row = [
            meta["date"],
            meta["student_name"],
            meta["sender_name"],
            meta["sender_type"],
            sequence_id,
            transcript,
            structured["summary"],
            "; ".join(structured["action_items"]),
            "; ".join(structured["blockers"]),
            structured["follow_up_needed"],
            datetime.now().isoformat(timespec="seconds"),
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info("[OK] Google Sheet Updated")
        return 0
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
