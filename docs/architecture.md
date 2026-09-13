# Architecture — Lenny Growth Assistant

## 1. Architecture Goals

The architecture is designed around five priorities:

1. Ground answers in the Lenny transcript knowledge base.
2. Keep chat sessions independent and persistent.
3. Support local Ollama and a cloud LLM through configuration.
4. Keep the agent capable but constrained through purpose-built tools.
5. Make the application simple to run, test, observe, and hand off.

The system favors explicit application boundaries over unnecessary framework dependencies.

---

## 2. Architectural Principles

### Grounded by Default

Product and growth answers should be supported by retrieved transcript evidence.

### Evidence Before Confidence

The system should evaluate retrieved evidence before generating a confident answer. If sufficient evidence is unavailable, it should acknowledge the limitation.

### Deterministic Retrieval

Retrieval, source selection, source metadata, and the evidence gate remain application-controlled rather than being left entirely to the model.

### Small Agent Tool Surface

The agent receives a small set of purpose-built tools rather than unrestricted access to the database, filesystem, or infrastructure.

### Configuration Over Code Changes

The LLM provider and model are selected through configuration so switching providers does not require changing application logic.

### Simple Infrastructure

PostgreSQL is used for application state and transcript retrieval data. pgvector provides vector search without introducing a second vector database.

---

## 3. High-Level Architecture

```text
+----------------------+
|      Web Frontend    |
|  Chat / Sources / UI |
+----------+-----------+
           |
           v
+----------------------+
|       FastAPI        |
| Routes / Validation  |
| Error Handling       |
+----------+-----------+
           |
           v
+----------------------+
| Application Services |
| Chat / Sessions      |
| Retrieval / Artifact |
+----------+-----------+
           |
           v
+----------------------+
|    Agent Runtime     |
|    Pi Coding Agent   |
+----------+-----------+
           |
     +-----+-----+
     |           |
     v           v
  Tools       LLM Provider
     |       +---------+---------+
     |       |                   |
     v       v                   v
 Retrieval  Ollama          Cloud LLM
     |
     v
 PostgreSQL + pgvector
```

The frontend communicates only with the FastAPI API. Application services own business rules and persistence access. The agent runtime coordinates model reasoning and approved tools.

---

## 4. Frontend

The frontend provides:

- Chat interface
- Session creation and session switching
- Conversation history
- Source display
- Provider/model visibility
- Ship30 output
- Artifact Viewer
- Loading states
- Error states

The UI should make the grounding model visible to users: answers can expose supporting episode/source information, while insufficient evidence is communicated explicitly.

The frontend does not directly access PostgreSQL, the transcript filesystem, or the LLM provider.

---

## 5. FastAPI Backend

FastAPI is the application boundary.

Responsibilities include:

- HTTP routing
- Request validation
- Response serialization
- Session validation
- Calling application services
- Structured errors
- Request/correlation IDs
- Health and readiness endpoints

Routes remain thin. Business logic belongs in application services rather than route handlers.

Conceptual layers:

```text
API Routes
    |
Schemas / Validation
    |
Application Services
    |
Repositories / Integrations
```

---

## 6. Agent Service

The primary agent runtime is **Pi Coding Agent**.

Pi is selected because the assignment requires a local Ollama demo and Pi provides a practical model/provider abstraction for local and cloud models while supporting skills and extensions.

The agent is responsible for:

- Understanding the user's intent
- Selecting an appropriate capability
- Calling approved tools
- Using retrieved evidence
- Producing a grounded response
- Invoking Ship30 when a writing task requires it
- Invoking artifact generation when requested or useful

The agent does not directly manipulate PostgreSQL or infrastructure.

The application controls which tools are available and what inputs they accept.

---

## 7. Tool Selection Architecture

The agent receives a small, explicit capability surface.

```text
                    Agent
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
 search_lenny     ship30        create_artifact
   _knowledge     writing
        |
        v
 Retrieval Service
```

### `search_lenny_knowledge`

Purpose:

- Search transcript evidence.
- Return ranked chunks.
- Return episode/source metadata.
- Return enough context for grounded generation.

The tool does not allow arbitrary SQL or filesystem access.

### Ship30 Writing Capability

Purpose:

- Turn grounded product/growth knowledge into a structured written piece.
- Follow the defined Ship30 writing principles.
- Preserve grounded claims.

### `create_artifact`

Purpose:

- Create Markdown or HTML/CSS output.
- Return artifact metadata for the UI.
- Pass HTML through the application's safety boundary before rendering.

---

## 8. Knowledge Base

The knowledge base is built from the Lenny Podcast transcript repository specified by the assignment.

The ingestion pipeline is:

```text
Transcript Source
      |
      v
Normalize / Parse
      |
      v
Episode Metadata
      |
      v
Chunk Transcript
      |
      v
Generate Embeddings
      |
      v
PostgreSQL + pgvector
      |
      v
Build / Refresh Retrieval Indexes
```

The repository's actual transcript format must be inspected before finalizing the parser.

Ingestion should be repeatable and observable.

Each ingestion run should record:

- status
- source/version information
- processed count
- failure count
- relevant error information

Chunking should preserve enough surrounding context for meaningful retrieval while avoiding excessively large evidence units.

Exact chunk size, overlap, transcript fields, and embedding model are implementation decisions that depend on the actual corpus.

---

## 9. Retrieval Architecture

The retrieval service combines lexical and semantic retrieval where both provide value.

```text
User Question
      |
      v
+-----------------------+
| Retrieval Service     |
+-----------+-----------+
            |
       +----+----+
       |         |
       v         v
     BM25     pgvector
       |         |
       +----+----+
            |
            v
       RRF Fusion
            |
            v
     Ranked Evidence
            |
            v
      Evidence Gate
```

### Lexical Retrieval

Useful for exact terms, names, product concepts, and distinctive phrases.

### Vector Retrieval

Useful for semantic similarity when the user's wording differs from the transcript wording.

### Reciprocal Rank Fusion

RRF combines independently ranked lexical and semantic results without requiring a separate vector database.

### Evidence Gate

The application evaluates whether retrieval produced sufficient evidence.

```text
Question
   |
   v
Retrieve Evidence
   |
   v
Evidence Sufficient?
   |             |
  YES            NO
   |             |
   v             v
Grounded       Transparent
Answer         Limitation
   |
   v
Sources
```

The evidence gate is an application-level rule, not merely a prompt instruction.

---

## 10. Source Tracing

Every retrieved chunk should retain enough metadata to trace the answer back to its source.

Conceptual metadata includes:

- episode ID
- episode title
- source URL
- published date where available
- chunk ID/index
- transcript timestamp where available
- relevance/ranking information

The API should return source references with grounded answers.

This allows users and evaluators to inspect where an answer came from.

---

## 11. Ingestion and Refresh

Ingestion should be idempotent or otherwise safe to repeat.

A refresh should:

1. Identify the source/version.
2. Parse and normalize transcript data.
3. Upsert episode metadata.
4. Generate deterministic chunks.
5. Generate/update embeddings.
6. Persist chunks and metadata.
7. Refresh retrieval indexes.
8. Record the ingestion result.

Failures should be recorded without silently presenting a partial corpus as fully successful.

---

## 12. PostgreSQL

PostgreSQL is the primary persistence layer for application state and transcript knowledge.

Conceptual entities include:

- `sessions`
- `messages`
- `episodes`
- `transcript_chunks`
- `ingestion_runs`

The sessions and messages tables persist independent conversations.

The episodes and transcript_chunks tables represent the transcript knowledge base.

The `transcript_chunks` table stores searchable transcript content, source metadata, and vector embeddings.

pgvector is used within PostgreSQL rather than introducing a separate vector database.

This keeps application state and retrieval data within one primary persistence system and reduces infrastructure complexity.

Database access should be performed through application services rather than directly through agent tools.

---

## 13. Conversation Context

Each chat session maintains its own conversation history.

```text
Session
  |
  +-- Message 1
  +-- Message 2
  +-- Message 3
  +-- ...
```

Follow-up questions use the current session context while still performing relevant knowledge retrieval when the answer depends on transcript evidence.

Conversation context must remain isolated between sessions.

The agent should receive the minimum context necessary to perform the current request rather than unrestricted access to unrelated sessions.

Persisted messages provide continuity across requests and allow the conversation to be reconstructed after application restarts.

---

## 14. Ship30 Writing Capability

Ship30 is implemented as a specialized writing capability available to the primary agent rather than as a separate autonomous agent.

The capability should produce approximately 1,250 words when the task calls for a full Ship30-style piece.

Required characteristics:

- Strong hook
- Clear narrative
- Skimmable headings
- Bullets where useful
- Selective bold emphasis
- Grounded claims
- Specific and useful takeaway

The writing capability should receive the user's intent and relevant grounded evidence.

It should not independently bypass the application's retrieval boundary.

The generated piece should distinguish source-backed claims from interpretation where appropriate.

---

## 15. Artifact Generation

Artifacts are generated through a dedicated application capability:

```text
create_artifact(
    type,
    title,
    content
)
```

Supported initial formats:

- Markdown
- HTML/CSS

The artifact service returns an artifact identifier and metadata that the frontend can display in the Artifact Viewer.

Generated HTML is treated as untrusted content.

The application should:

- Sanitize or restrict dangerous HTML.
- Prevent arbitrary script execution where practical.
- Avoid server-side execution of generated content.
- Avoid exposing application secrets.
- Isolate the viewer from the main application where practical.
- Document which HTML/CSS behaviors are permitted or blocked.

The first version should avoid unnecessary artifact editing complexity.

---

## 16. API Contracts

Initial API surface:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/health/ready` | Dependency readiness |
| POST | `/api/sessions` | Create session |
| GET | `/api/sessions/{session_id}` | Retrieve session |
| POST | `/api/sessions/{session_id}/messages` | Send message |
| POST | `/api/sessions/{session_id}/artifacts` | Create artifact |
| GET | `/api/artifacts/{artifact_id}` | Retrieve artifact |

Request schemas should validate required fields and reject malformed input.

Successful message responses should expose, where applicable:

- session ID
- assistant message
- source references
- provider/model metadata
- artifact metadata

The exact wire schema is finalized during implementation and tested as an API contract.

---

## 17. Error Handling and Resilience

Errors use a consistent structure:

```json
{
  "error": {
    "code": "RETRIEVAL_UNAVAILABLE",
    "message": "The knowledge base is temporarily unavailable.",
    "request_id": "..."
  }
}
```

Initial error codes include:

- `VALIDATION_ERROR`
- `SESSION_NOT_FOUND`
- `RETRIEVAL_UNAVAILABLE`
- `NO_EVIDENCE`
- `LLM_UNAVAILABLE`
- `LLM_TIMEOUT`
- `OLLAMA_UNAVAILABLE`
- `DATABASE_UNAVAILABLE`
- `ARTIFACT_GENERATION_FAILED`
- `INTERNAL_ERROR`

Expected behavior:

| Failure | Behavior |
|---|---|
| Missing cloud key | Explain configuration requirement |
| Ollama unavailable | Return clear dependency error |
| Model timeout | Return structured timeout error |
| Empty retrieval | Do not fabricate; acknowledge insufficient evidence |
| PostgreSQL failure | Return dependency error and log diagnostic context |
| Artifact failure | Return artifact-specific error |
| Invalid request | Return validation error |
| Unknown session | Return session-not-found error |

Internal stack traces and credentials must not be exposed to users by default.

---

## 18. Observability

The backend should use structured logs.

Common fields:

- timestamp
- level
- event
- request_id
- session_id
- duration_ms
- provider
- model
- status
- error_code

Retrieval events should additionally capture appropriate operational metrics such as:

- retrieval count
- lexical result count
- vector result count
- retrieval latency
- evidence status

Agent events may capture:

- tool name
- tool-call status
- tool latency

Logs must not contain API keys, database credentials, or unnecessary sensitive conversation content.

The request/correlation ID should be propagated across:

```text
API
 |
Agent
 |
Tool
 |
Retrieval
 |
Database / LLM
 |
Response
```

---

## 19. Security Architecture

Security boundaries include:

### Secrets

- No secrets committed to Git.
- `.env` is ignored.
- `.env.example` documents required configuration.
- API keys are loaded from environment/configuration.

### Agent Tools

Tools are explicitly allow-listed.

The agent must not receive unrestricted access to:

- PostgreSQL
- filesystem
- deployment infrastructure
- arbitrary shell commands

### Session Isolation

Every message operation validates the target session.

Conversation context must never be mixed between sessions.

### Generated HTML

Generated HTML is untrusted and must pass through the artifact security boundary before rendering.

### Error Responses

Production-facing errors should not expose stack traces, internal paths, credentials, or raw infrastructure details.

---

## 20. Deployment Topology

The target local deployment is:

```text
+----------------+
|    Frontend    |
+-------+--------+
        |
        v
+----------------+
|    FastAPI     |
+---+--------+---+
    |        |
    v        v
PostgreSQL  Ollama
 +pgvector
    ^
    |
Cloud LLM (alternative provider)
```

The project should support a one-command startup, ideally through Docker Compose.

The handoff documentation should explain:

1. Prerequisites.
2. Environment configuration.
3. Database startup.
4. Ollama startup.
5. Ollama model setup.
6. Optional cloud provider configuration.
7. Transcript ingestion.
8. Application startup.
9. Health checks.
10. Troubleshooting.

---

## 21. Testing Strategy

Testing is organized around the highest-risk behavior.

### API Tests

- Request validation
- Session creation
- Session isolation
- Message handling
- Structured errors
- Health endpoints

### Persistence Tests

- Sessions
- Messages
- Episodes
- Transcript chunks
- Ingestion runs

### Retrieval Tests

- Relevant chunk retrieval
- Source metadata
- Lexical/vector ranking
- Empty retrieval
- Evidence gate behavior

### Agent Tests

- Grounded question routing
- Follow-up handling
- Ship30 routing
- Artifact routing
- Unsupported question behavior
- Tool input validation

### Provider Tests

- Ollama configuration
- Cloud configuration
- Provider switching
- Unavailable provider errors

### Artifact Tests

- Markdown generation
- HTML generation
- Sanitization/restriction
- Artifact retrieval

### Manual UI Test Plan

Verify:

1. Create a session.
2. Ask a grounded question.
3. Inspect sources.
4. Ask a follow-up.
5. Ask an unsupported question.
6. Request Ship30 content.
7. Generate an artifact.
8. Open the Artifact Viewer.
9. Test loading/error states.
10. Create a second session and confirm isolation.

---

## 22. Configuration and Environment

Configuration is environment-driven.

Initial configuration:

```text
APP_ENV
LOG_LEVEL
DATABASE_URL
LLM_PROVIDER
OLLAMA_BASE_URL
OLLAMA_MODEL
ANTHROPIC_API_KEY
EMBEDDING_MODEL
```

The active provider/model should be visible to the application where appropriate.

Switching between Ollama and the cloud provider should not require application-code changes.

Provider precedence and fallback behavior must be explicit. The application should not silently switch providers in a way that surprises users or evaluators.

No secret values belong in source control.

---

## 23. Key Technical Trade-offs

### PostgreSQL + pgvector

Chosen instead of a separate vector database because the assignment already requires PostgreSQL and the knowledge base can remain within the same persistence system.

### Hybrid Retrieval

Lexical plus vector retrieval provides complementary matching behavior without adding another search infrastructure dependency.

### Deterministic Retrieval Boundary

Keeping retrieval outside unconstrained model reasoning makes grounding and source tracing easier to test and defend.

### Small Agent Tool Surface

A small tool set reduces accidental behavior, security risk, and debugging complexity.

### Pi Coding Agent

Pi is selected over Claude Agent SDK because the mandatory local Ollama demonstration and provider flexibility are central assignment requirements. Claude Agent SDK is strongly aligned with Claude's own agent runtime, while Pi provides a cleaner architecture for supporting Ollama alongside a cloud provider.

This is a deliberate trade-off: local model tool-calling quality must be tested and the demo should use a model that performs reliably enough for the selected tool workflow.

### Avoiding Unnecessary Frameworks

LangChain, LlamaIndex, a second vector database, Redis, Elasticsearch, or similar dependencies should not be introduced unless a measured project requirement justifies them.

---

## 24. End-to-End Request Flows

### Grounded Question

```text
User
  |
  v
FastAPI
  |
  v
Session Context
  |
  v
Agent
  |
  v
search_lenny_knowledge
  |
  v
Retrieval Service
  |
  v
Evidence Gate
  |
  +---- insufficient ----> Transparent limitation
  |
 sufficient
  |
  v
Agent generates grounded answer
  |
  v
Sources attached
  |
  v
Persist message
  |
  v
Frontend
```

### Ship30 Request

```text
User
  |
  v
Agent
  |
  v
Retrieve relevant evidence
  |
  v
Ship30 capability
  |
  v
~1,250-word structured piece
  |
  v
Persist / return response
```

### Artifact Request

```text
User
  |
  v
Agent
  |
  v
create_artifact
  |
  v
Artifact Service
  |
  v
Sanitize / restrict HTML if required
  |
  v
Persist artifact
  |
  v
Artifact Viewer
```

### Follow-up Question

```text
User Follow-up
      |
      v
Current Session Context
      |
      v
Relevant Retrieval
      |
      v
Evidence Gate
      |
      v
Grounded Response
      |
      v
Persist Message
```

The follow-up uses conversation context for continuity but does not treat prior conversation text as a substitute for transcript evidence.

---

## 25. Architecture Summary

The system is intentionally layered:

```text
UI
 |
 v
FastAPI API
 |
 v
Application Services
 |
 v
Pi Coding Agent
 |
 +-------------------+
 |                   |
 v                   v
Purpose-built     Model Providers
Tools             /          \
 |                Ollama     Cloud
 v
Retrieval Service
 |
 v
PostgreSQL + pgvector
```

The central design decision is that **the agent reasons over controlled capabilities, while the application owns grounding, persistence, security, and operational boundaries**.

This keeps the system explainable and testable while still satisfying the assignment's agentic requirements.
