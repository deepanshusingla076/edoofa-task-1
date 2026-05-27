# Edoofa Technical Round - Voice Note Operations Prototype

## 1) Problem Statement

Edoofa supports more than 2,500 students through individual WhatsApp groups.
Operationally critical updates, including student progress, required actions,
blockers, and follow-ups, are frequently shared as voice notes. This creates
three recurring challenges:

- Teams must repeatedly listen to audio to retrieve key details.
- Follow-ups can be missed due to unstructured information flow.
- There is no consistent student-level historical record.

## 2) Constraints Considered

- **No WhatsApp Group API access:** Group messages cannot be programmatically
  ingested.
- **Multiple sender types:** Students, parents, mentors, and staff send notes
  in mixed sequence.
- **High note volume:** Many notes per student per day require deterministic
  sequencing (for example, `VN-001`, `VN-002`).
- **Operator simplicity:** Workflow must remain easy for non-technical ops
  users.
- **Cost sensitivity:** Prototype is designed on free-tier tooling.

## 3) Proposed Workflow

```text
WhatsApp Web (manual download) -> Local audio file -> Python pipeline
-> Local Whisper transcription -> Gemini structuring -> Google Sheets logging
```

1. Operations user downloads a voice note from WhatsApp Web (manual ingestion
   for prototype).
2. The script reads the audio and extracts student/sender metadata from the
   filename, with fallback defaults.
3. **Whisper (local CPU)** transcribes speech to text.
4. **Gemini** converts transcript into structured fields (summary, actions,
   blockers, follow-up flag).
5. **Google Sheets** appends a row and assigns a per-student, per-day sequence
   ID.

## 4) Minimal Architecture

| Layer | Tool | Responsibility |
| --- | --- | --- |
| Ingestion | WhatsApp Web + local file drop | Practical workaround for API limitation |
| Transcription | `openai-whisper` (local) | Speech-to-text conversion on CPU |
| Structuring | Gemini 1.5 Flash | Information extraction into consistent JSON |
| Storage | `gspread` + service account | Searchable and shareable operations log |

**Logged fields:** Date, Student Name, Sender Name, Sender Type, Voice Note
Sequence ID, Transcript, Summary, Action Items, Blockers, Follow-Up Needed,
Timestamp.

## 5) Design Rationale

- **Speed of execution:** Single-script implementation (`app.py`) minimizes
  setup overhead.
- **Demo reliability:** Fewer components improve predictability and reduce
  failure points.
- **Zero-cost prototype:** Fully aligned with free-tier evaluation constraints.
- **Scalable pathway:** Can later extend through WhatsApp Web automation (for
  example, Playwright), folder watchers, or orchestration tools (n8n/Zapier)
  without redesigning the core pipeline.

## 6) Suggested Success Metrics (Next Phase)

- Voice notes processed per day
- Average processing turnaround time
- Percentage of notes flagged for follow-up
- Blocker frequency per student or cohort
