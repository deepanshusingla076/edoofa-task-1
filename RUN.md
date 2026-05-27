# How to Run (5 minutes)

## What you need (all free)

| Item | Status |
|------|--------|
| Gemini API key | In `.env` |
| Google service account | `service_account.json` |
| Google Sheet | Create and share (see below) |
| Voice note file | `.ogg` or `.mp3` from WhatsApp |

## Step 1 — Install (one time)

Open PowerShell in this folder:

```powershell
cd C:\Users\deepa\OneDrive\Desktop\edoofa
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

First run downloads Whisper model (~150MB). Needs internet once.

## Step 2 — Google Sheet (one time)

1. Go to [Google Sheets](https://sheets.google.com) → **Blank spreadsheet**
2. Name it exactly: **Student Voice Notes**  
   (or change `GOOGLE_SHEET_NAME` in `.env` to your name)
3. Click **Share**
4. Add this email as **Editor**:
   ```
   edoofa-bo@edoofa-ai.iam.gserviceaccount.com
   ```
5. Click **Send**

## Step 3 — Get a voice note

1. Open WhatsApp Web → student group
2. Download a voice note (`.ogg` or `.mp3`)
3. Save in this folder, e.g. `voice.ogg`

**Optional** — auto-fill student/sender from filename:

```
arjun_parent_meena_2026-05-27.ogg
```

Format: `student_senderType_senderName_YYYY-MM-DD.ext`

## Step 4 — Run

```powershell
.venv\Scripts\Activate.ps1
python app.py --audio voice.ogg
```

## Expected output

```
[✓] Audio Loaded
[✓] Transcript Generated
[✓] AI Summary Generated
[✓] Google Sheet Updated
```

Open your Google Sheet — new row with transcript, summary, action items, VN-001, etc.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Spreadsheet not found` | Sheet name must match `.env` exactly |
| `Permission denied` | Share sheet with service account email |
| `Missing env var` | Check `.env` exists in project root |
| Whisper slow | Normal on CPU; use short audio for demo |
| Gemini error | Check API key at [AI Studio](https://aistudio.google.com) |

## Screen recording checklist (submission)

1. Show WhatsApp Web voice note
2. Run `python app.py --audio ...`
3. Show terminal ✓ messages
4. Show new row in Google Sheet

Email: **techsupport@edoofa.com**
