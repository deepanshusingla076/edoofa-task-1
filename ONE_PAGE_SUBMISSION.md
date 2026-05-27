# Edoofa Technical Round — Voice Note Ops Prototype (One Page)

## Problem Understanding

Edoofa manages 2,500+ students via individual WhatsApp groups. Critical updates (progress, actions, blockers, follow-ups) are sent as voice notes and are hard to search, reference, or track. Ops teams must re-listen to audio; follow-ups get missed; there is no structured student-level record.

## Key Constraints

- **No WhatsApp Group API** — cannot ingest messages programmatically from groups.
- **Mixed senders** — students, parents, mentors, and Edoofa staff send notes in arbitrary order.
- **Volume** — many notes per student per day; need sequence IDs (VN-001, VN-002).
- **Non-technical users** — solution must be simple to operate.
- **Cost** — prototype uses only free tools (local Whisper, Gemini free tier, Google Sheets).

## Proposed Workflow

```
WhatsApp Web (manual download) → Local audio file → Python script
    → Local Whisper (transcribe) → Gemini (structure) → Google Sheet (store)
```

1. Ops downloads voice note from student’s WhatsApp group (simulated ingestion).
2. Script loads audio; parses student/sender from filename or defaults.
3. **Whisper (CPU)** transcribes audio locally — no paid API.
4. **Gemini** returns JSON: summary, action items, blockers, follow-up flag.
5. **Google Sheets** appends one row; sequence ID increments per student + date.

## Architecture (minimal)

| Layer | Tool | Role |
|-------|------|------|
| Ingestion | WhatsApp Web + file drop | Practical workaround for API gap |
| Transcription | openai-whisper (local) | Speech-to-text on CPU |
| Intelligence | Gemini 1.5 Flash | Structured extraction |
| Storage | gspread + service account | Searchable ops log |

**Data columns:** Date, Student Name, Sender Name, Sender Type, Voice Note Sequence ID, Transcript, Summary, Action Items, Blockers, Follow Up Needed, Timestamp.

## Reasoning

- **Simplicity over scale** — single `app.py`, no DB/frontend/auth for 1-hour prototype.
- **Reliability for demo** — fewer moving parts; clear terminal status.
- **Free stack** — sustainable for assessment without billing.
- **Scalability path** — later: Playwright auto-download from WhatsApp Web, folder watcher, or n8n/Zapier trigger; same pipeline.

## Metrics (future)

- Notes processed per day, avg turnaround time, % with follow-up flagged, blockers per student.
