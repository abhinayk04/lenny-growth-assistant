# Agent Transcript 04 — Provider Error & Fallback Handling

**Session ID**: `e9999999-0000-4000-8000-111122223333`  
**Timestamp**: `2026-09-15 19:46:00 UTC`  
**Provider**: `Ollama (Unavailable)`  
**Status**: `SERVICE_UNAVAILABLE_HANDLED`  

---

### Request
```json
POST /api/sessions/e9999999-0000-4000-8000-111122223333/messages
{
  "role": "user",
  "content": "How do top growth teams structure their experiments?"
}
```

### Retrieval Phase
- Retrieval & Evidence Gate completed successfully (`sufficient = True`).

### Agent Execution Failure
- Ollama service was temporarily shut down or unreachable on `http://localhost:11434`.
- Pi CLI subprocess timed out / connection refused.
- Backend caught `RuntimeError` ("OLLAMA_UNAVAILABLE: Failed to connect to Ollama").

### Error Response (HTTP 503 Service Unavailable)
```json
{
  "error": {
    "code": "OLLAMA_UNAVAILABLE",
    "message": "Failed to connect to Ollama at http://localhost:11434: [WinError 10061] No connection could be made because the target machine actively refused it",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```
*Note: No internal stack traces or database credentials were leaked to the client response.*
