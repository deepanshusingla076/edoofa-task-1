# Edoofa Voice Note Ops Prototype

A lightweight Python pipeline that converts voice-note audio into structured
operations updates and stores the result in Google Sheets.

## Overview

This prototype processes a local audio file and runs the following flow:

1. Transcribe audio with local Whisper (CPU).
2. Extract structured insights with Gemini.
3. Append one searchable row in Google Sheets.

The goal is to provide an easy, low-cost workflow with minimal setup.

## Tech Stack

- Python 3.10+
- `openai-whisper` for transcription
- Gemini Flash API for summarization and extraction
- `gspread` + Google service account for Google Sheets writes

## Project Files

- `app.py` - main processing pipeline
- `requirements.txt` - dependencies
- `.env.example` - environment variable template
- `ONE_PAGE_SUBMISSION.md` - one-page technical summary
- `RUN.md` - quick run reference

## Setup

### 1) Create virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Create `.env` from `.env.example` and fill:

```env
GEMINI_API_KEY=your_key_here
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
GOOGLE_SHEET_NAME=Student Voice Notes
DEFAULT_SENDER_TYPE=Parent
DEFAULT_SENDER_NAME=WhatsApp Group Member
DEFAULT_STUDENT_NAME=Unknown Student
```

### 4) Configure Google Sheets access

1. Create a Google service account in Google Cloud.
2. Download the credentials JSON as `service_account.json` in project root.
3. Create/open your target Google Sheet.
4. Share that sheet with the service account email as **Editor**.

## Usage

Run the script with any supported local audio file (`.ogg`, `.mp3`, etc.):

```powershell
python app.py --audio path\to\voice_note.ogg
```

Expected success logs:

```text
[OK] Audio Loaded
[OK] Transcript Generated
[OK] AI Summary Generated
[OK] Google Sheet Updated
```

## Metadata and Sequencing

- If the audio filename matches this format, metadata is auto-parsed:
  `student_senderType_senderName_YYYY-MM-DD.ext`
- Otherwise, defaults from `.env` are used.
- Sequence IDs are generated per student per date: `VN-001`, `VN-002`, etc.

## Output Columns

The pipeline appends:

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

## Troubleshooting

- `Missing env var`: verify `.env` keys are present.
- `Spreadsheet not found`: confirm `GOOGLE_SHEET_NAME` matches exactly.
- Permission errors: re-share sheet with service account email.
- Slow first run: Whisper model download and CPU inference can take time.
