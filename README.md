# Edoofa Free Ops Prototype

Beginner-friendly, fully free prototype:
- local Whisper (CPU) for transcription
- Gemini free API for structuring updates
- Google Sheets for storage

## Project Structure

- `app.py`
- `requirements.txt`
- `.env.example`
- `README.md`

## 5-Minute Setup

1) Create and activate virtual env:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Create `.env` from `.env.example` and fill values:

```env
GEMINI_API_KEY=your_key_here
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
GOOGLE_SHEET_NAME=Student Voice Notes
DEFAULT_SENDER_TYPE=Parent
DEFAULT_SENDER_NAME=WhatsApp Group Member
DEFAULT_STUDENT_NAME=Unknown Student
```

4) Google Sheets setup (one-time):
- create service account in Google Cloud
- download key JSON as `service_account.json`
- share your target Google Sheet with service-account email

## Run

```bash
python app.py --audio your_voice_note.ogg
```

Expected terminal output:

```text
[✓] Audio Loaded
[✓] Transcript Generated
[✓] AI Summary Generated
[✓] Google Sheet Updated
```

## WhatsApp Ingestion (Simple Demo Method)

WhatsApp Group has no direct API. Use simulated ingestion:
1. Open WhatsApp Web
2. Download voice note manually
3. Run script with downloaded audio file

Optional filename format for auto metadata:
`student_senderType_senderName_YYYY-MM-DD.ogg`

Example:
`arjun_parent_meena_2026-05-27.ogg`

If filename does not match this format, default `.env` values are used.

## Google Sheet Columns

The script writes:
1. Date
2. Student Name
3. Sender Name
4. Sender Type
5. Voice Note Sequence ID
6. Transcript
7. Summary
8. Action Items
9. Blockers
10. Follow Up Needed
11. Timestamp

Sequence IDs auto-increment per same Date + Student:
`VN-001`, `VN-002`, `VN-003`, ...

## One-Page Architecture Explanation

Single-file flow in `app.py`:
1. Load audio from local file (simulated WhatsApp ingestion)
2. Transcribe locally with Whisper (`openai-whisper`) on CPU
3. Send transcript to Gemini and request strict JSON output
4. Connect to Google Sheet using service account (`gspread`)
5. Compute next sequence ID for student/day
6. Append one row with transcript + structured fields

Design goal: minimal moving parts, max demo reliability.

## Demo Script (Read While Recording)

1. "This is a free Edoofa ops prototype with no paid APIs."
2. "I downloaded a voice note from WhatsApp Web."
3. "Now I run: `python app.py --audio your_voice_note.ogg`"
4. "Whisper transcribes locally on CPU."
5. "Gemini creates summary, action items, blockers, and follow-up."
6. "The update is appended into Google Sheets with sequence ID."
