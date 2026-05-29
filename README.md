# TabSnap

**Hear a riff. Get the tab.**

Upload 10–30 seconds of guitar audio and get a playable guitar tab back — with confidence scores, MIDI export, and a correction editor.

## Quick Start (Local Dev)

Prerequisites: Python 3.11+, Node.js 18+, FFmpeg

```bash
git clone https://github.com/MirrorDNA-Reflection-Protocol/tabsnap.git
cd tabsnap

# Install Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/api/requirements.txt -r services/worker/requirements.txt

# Install frontend deps
cd apps/web && npm install && cd ../..

# Run
./dev.sh
```

Open **http://localhost:3000** — upload a guitar clip and get a tab.

## How It Works

```
Audio file (.mp3/.wav/.m4a)
  → FFmpeg normalizes to WAV
  → Basic Pitch (Spotify ML) converts to MIDI
  → Fretboard solver finds playable string/fret positions
  → ASCII tab renderer outputs standard guitar tab
  → Confidence scorer rates the result honestly
```

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js |
| API | FastAPI |
| Worker | Python (Basic Pitch, librosa) |
| Database | SQLite (local) / Postgres (prod) |
| Queue | Sync (local) / Redis + RQ (prod) |

## Docker (Production)

```bash
docker compose up
```

Starts: Postgres, Redis, API, Worker, Web on ports 5432, 6379, 8000, 3000.
