# Lenny Growth Assistant

Conversational product and growth assistant grounded strictly in Lenny's Podcast transcripts.

---

## 1. Overview & Purpose

The **Lenny Growth Assistant** helps product managers, growth leads, and founders query real insights from over 300+ Lenny's Podcast episodes without hallucinations.

### Key Capabilities:
1. **Grounded Q&A**: Answers product questions backed strictly by transcript evidence with source citations.
2. **Evidence Gate**: Rejects out-of-domain/unsupported questions with a transparent limitation notice instead of fabricating advice.
3. **Session-Aware Context**: Remembers conversation history within independent sessions for natural multi-turn follow-ups.
4. **Ship 30 for 30 Writing Skill**: Generates ~1,250-word structured growth essays (Hook, Narrative, Skimmable Headings, Bullets, Selective Bold, Takeaways).
5. **Artifact Generation & Viewer**: Creates Markdown or HTML growth framework artifacts rendered in a side-by-side split screen viewer.
6. **Configurable Model Providers**: Native local Ollama (`qwen3:4b`) support alongside Cloud LLMs (Anthropic Claude).

---

## 2. Architecture

```text
+--------------------------------------------------------+
|                   Web Frontend (UI)                    |
|   Chat Window | Citations | Side-by-Side Artifacts     |
+---------------------------+----------------------------+
                            | HTTP / REST
                            v
+--------------------------------------------------------+
|                   FastAPI Backend                      |
|   Session Persistence | Structured Error Handling      |
+---------------------------+----------------------------+
                            |
                            v
+--------------------------------------------------------+
|                 Retrieval Pipeline                     |
|   Lexical BM25 + Vector Search (pgvector) + RRF        |
|                  --> Evidence Gate                     |
+---------------------------+----------------------------+
                            | Evidence & Prompt
                            v
+--------------------------------------------------------+
|                     Agent Layer                        |
|       Pi Coding Agent (@mariozechner/pi-coding-agent)  |
|            (Ollama / Anthropic Cloud Fallback)         |
+--------------------------------------------------------+
```

---

## 3. Tech Stack

- **Backend**: FastAPI, Python 3.13+
- **Agent Layer**: Pi Coding Agent (`@mariozechner/pi-coding-agent`)
- **Database & Retrieval**: PostgreSQL 17 + `pgvector` (HNSW indexing)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384d)
- **Local LLM**: Ollama (`qwen3:4b` with reasoning disabled for low latency)
- **Cloud LLM**: Anthropic API (`claude-3-5-sonnet`)
- **Frontend**: Standalone HTML5 / CSS3 / Vanilla JS (No build step required)

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Docker Desktop (for PostgreSQL + pgvector)
- Node.js 18+ (for `@mariozechner/pi-coding-agent`)
- Ollama (installed locally with `qwen3:4b`)

### Quick Start Guide

#### 1. Clone & Configure Environment
```bash
cp .env.example .env
```

#### 2. Start PostgreSQL Database
```bash
docker compose up -d
```

#### 3. Setup Transcripts Corpus (If not already present)
```bash
python scripts/setup_transcripts.py
```
*(Clones transcript repository into `data/transcripts/source/`)*

#### 4. Run Ingestion Pipeline (303 episodes / 4732 chunks)
```bash
python scripts/ingest.py
```

#### 5. Ensure Ollama Local Model
```bash
ollama pull qwen3:4b
```

#### 6. Start FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### 7. Open Frontend UI
Open `frontend/index.html` directly in your browser.

---

## 5. Environment Variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Application environment |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DATABASE_URL` | `postgresql+psycopg://lenny:lenny_dev_password@localhost:5432/lenny` | PostgreSQL connection string |
| `LLM_PROVIDER` | `ollama` | Provider selection (`ollama` or `anthropic`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `qwen3:4b` | Ollama model tag |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API Key (Optional) |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Cloud LLM model tag |

---

## 6. API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service liveness & provider info |
| `GET` | `/health/ready` | PostgreSQL readiness check |
| `POST` | `/api/sessions` | Create new independent chat session |
| `GET` | `/api/sessions/{id}` | Retrieve session metadata |
| `POST` | `/api/sessions/{id}/messages` | Send user message & get grounded response |
| `GET` | `/api/sessions/{id}/messages` | Retrieve session message history |
| `POST` | `/api/sessions/{id}/ship30` | Generate ~1,250-word Ship30 growth essay |
| `POST` | `/api/sessions/{id}/artifacts` | Create Markdown or HTML artifact |
| `GET` | `/api/artifacts/{id}` | Retrieve generated artifact |

---

## 7. Retrieval, Grounding & Evidence Gate

1. **Hybrid Search**: Combines full-text BM25 keyword matching with pgvector cosine similarity search.
2. **Reciprocal Rank Fusion (RRF)**: Merges lexical and vector rankings deterministically.
3. **Evidence Gate**: Evaluates similarity scores against `MIN_VECTOR_SIMILARITY = 0.45`.
   - If similarity < 0.45: Returns transparent limitation ("I couldn't find enough evidence in Lenny's transcripts to answer that confidently.").
   - If similarity >= 0.45: Passes top 4 evidence chunks to agent.

---

## 8. Ship 30 for 30 Writing Skill

Requesting a Ship30 piece triggers a dedicated skill pipeline that formats retrieved transcript evidence into a ~1,250-word growth essay featuring:
- Attention-grabbing Hook
- Narrative structure
- Skimmable H2 Headings
- Bullet points
- Selective bold emphasis
- Practical takeaway summary

---

## 9. Artifact Viewer & Security Boundary

- Artifacts are generated as Markdown or clean HTML/CSS.
- **Security Boundary**: Server-side HTML sanitization strips `<script>` tags, inline event attributes (`onclick`, `onload`), and `javascript:` URIs.
- **Isolated Rendering**: HTML artifacts render inside an `<iframe>` sandbox (`sandbox="allow-same-origin"`).

---

## 10. Manual UI Test Plan & 2-3 Minute Demo Flow

1. **Launch App**: Open `frontend/index.html`. Verify header displays `Provider: Ollama (qwen3:4b)`.
2. **Ask Grounded Question**: Type *"How can we improve product retention?"* and press Enter.
   - Verify: Response returned in ~3-6 seconds.
   - Verify: Source cards displayed with clickable links.
   - Verify: Green badge "Grounded in Transcripts".
3. **Multi-Turn Follow-Up**: Ask *"What about onboarding?"*.
   - Verify: Answer references previous context while incorporating fresh onboarding evidence.
4. **Unsupported Question**: Ask *"What is the capital of France?"*.
   - Verify: Yellow badge "Insufficient Evidence" and transparent limitation message.
5. **Generate Ship30 Essay**: Click *"Ship30 Essay"* button.
   - Verify: ~1,250-word formatted essay appears in the right-side Artifact Viewer.
6. **Generate Artifact**: Click *"Create Artifact"*.
   - Verify: Structured Markdown artifact appears in Artifact Viewer.

---

## 11. Automated Testing

Run unit & integration test suite:
```bash
pytest
```

Includes coverage for:
- Transcript parsing & chunking
- Evidence gate thresholding
- Session creation & isolation
- Multi-turn history formatting
- Ship30 generation endpoint
- Artifact creation & retrieval
- HTML security sanitization
- Structured error handling

---

## 12. Design Trade-offs & Known Limitations

- **Ollama Reasoning Traces**: `qwen3:4b` defaults to reasoning. To ensure demo speed, reasoning traces (`<think>`) are automatically stripped, keeping latency under 8 seconds.
- **Subprocess Agent Integration**: Pi Coding Agent CLI (`pi.cmd` / `pi`) is invoked via subprocess with standard fallbacks to keep execution reliable across environments.
- **Local Transcripts Storage**: Raw transcript files (`data/transcripts/source/`) are ignored by Git per assignment instructions. Use `python scripts/setup_transcripts.py` to retrieve them.
