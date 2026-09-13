# Lenny Growth Assistant — Product Requirements Document



## 1. Product Overview



### Product



**The Lenny Growth Assistant**



An internal AI-powered conversational assistant for product and growth teams that uses Lenny's Podcast transcripts as its knowledge base.



The assistant helps users:



1\. Ask product and growth questions and receive grounded answers.

2\. Transform Lenny-derived insights into reusable written content using a dedicated Ship 30 for 30 skill.

3\. Generate Markdown or HTML/CSS artifacts that are rendered inside the application.



The product is designed so that users do not need to understand prompts, models, retrieval systems, or infrastructure.



---



## 2. Problem Statement



Product and growth teams can gain valuable insights from Lenny's Podcast transcripts, but extracting trustworthy information and turning those insights into reusable content or artifacts can require significant manual effort.



The assistant should reduce this effort while maintaining trust.



The central product principle is:



> If the Lenny knowledge base does not contain sufficient supporting evidence, the assistant should acknowledge the limitation instead of fabricating an answer.



---



## 3. Target User



### Primary User



Internal product and growth professionals.



### User Needs



Users should be able to:



- Quickly find relevant product and growth insights.

- Ask follow-up questions without losing conversation context.

- Verify answers through transcript/source references.

- Turn insights into useful written content.

- Turn conversations into visual or structured artifacts.

- Use the product without understanding the underlying AI infrastructure.



---



## 4. User Jobs



### Job 1 — Ask a Product/Growth Question



Example:



> What are the most important principles for improving product activation?



Expected behavior:



Question -> retrieve relevant transcript evidence -> generate grounded answer -> show sources.



---



### Job 2 — Generate Reusable Written Content



Example:



> Turn these insights into a Ship 30 for 30 style article.



Expected behavior:



Conversation/evidence -> dedicated Ship30 skill -> approximately 1,250-word formatted content.



---



### Job 3 — Generate an Artifact



Example:



> Create a product-growth framework based on this discussion.



Expected behavior:



Conversation/evidence -> artifact generation -> Markdown or HTML/CSS -> safe rendering -> Artifact Viewer.



---



## 5. Goals



### Product Goals



- Provide trustworthy, transcript-grounded answers.

- Preserve context within each conversation session.

- Allow independent new conversations.

- Make relevant sources visible.

- Generate reusable written content.

- Generate renderable artifacts.

- Make the local Ollama model usable for the demonstration.



### Engineering Goals



- FastAPI backend.

- PostgreSQL persistence.

- Retrieval over Lenny transcripts.

- Agent-based architecture.

- Configurable LLM providers.

- Local Ollama support.

- At least one cloud LLM provider.

- Automated tests for critical functionality.

- Clear errors and health checks.

- Reproducible local setup.

- Clear documentation and handoff.



---



## 6. Success Metrics



These are project-level targets rather than requirements explicitly specified by the assignment.



| Metric | Target |

|---|---:|

| Questions with supporting evidence that return relevant sources | >=90% |

| Unsupported evaluation questions that avoid fabricated answers | 100% |

| Critical acceptance flows that pass | 100% |

| Fresh evaluator can run the documented local setup | Yes |

| Ollama local demonstration works | Yes |

| Ship30 generation works | Yes |

| Artifact rendering works | Yes |



---



## 7. Assumptions



1\. The primary users are internal product/growth professionals.

2\. Lenny's Podcast transcripts are the authoritative knowledge source for transcript-grounded answers.

3\. The assistant should not present unsupported claims as being derived from Lenny.

4\. Authentication/enterprise SSO is outside the MVP unless required for deployment.

5\. Ollama is the primary local demonstration provider.

6\. One cloud LLM provider is sufficient for the MVP.

7\. PostgreSQL will be used for application persistence and retrieval infrastructure.

8\. The system should support independent conversation sessions.

9\. Generated HTML is untrusted content and must be safely rendered.



---



## 8. Scope



### 8.1 In Scope



- Conversational chat.

- New independent sessions.

- Conversation persistence.

- PostgreSQL.

- Lenny transcript ingestion.

- Transcript chunking and indexing.

- Retrieval/RAG.

- Source tracing/citations.

- Follow-up questions.

- Ollama.

- Cloud LLM.

- Configurable model provider.

- Agent layer.

- Dedicated Ship30 skill.

- Markdown artifacts.

- HTML/CSS artifacts.

- Artifact Viewer.

- Safe HTML rendering.

- Structured errors.

- Health endpoints.

- Logging/observability.

- Automated tests.

- Docker/local startup.

- README and handoff documentation.

- Agent development transcripts.



### 8.2 Out of Scope



- Enterprise SSO.

- Billing and payments.

- Mobile application.

- Complex administrative dashboard.

- Advanced enterprise permission systems.

- Multi-tenant enterprise controls.

- Supporting many cloud LLM providers.

- Advanced analytics.



---



## 9. High-Level User Flow



### Conversational Flow



User opens the application.



v



Creates or selects a conversation.



v



User asks a product/growth question.



v



Frontend sends the request to FastAPI.



v



FastAPI passes the request to the agent.



v



Agent retrieves relevant transcript evidence.



v



Evidence is passed to the selected LLM.



v



Assistant generates a grounded response.



v



Relevant sources are displayed.



v



Conversation is persisted.



---



## 10. Follow-Up Flow



User asks an initial question.



v



Assistant answers using retrieved evidence.



v



User asks a follow-up.



v



The existing session context is preserved.



v



Agent uses conversation context plus relevant retrieval.



v



Assistant responds.



A new chat must not inherit context from another session.



---



## 11. Unsupported Question Flow



User asks a question that cannot be sufficiently supported by the Lenny knowledge base.



v



Retrieval returns insufficient evidence.



v



Assistant does not fabricate a Lenny-derived answer.



v



Assistant clearly communicates that sufficient supporting information was not found.



---



## 12. Ship30 Content Flow



User requests reusable written content.



v



Agent identifies the Ship30 task.



v



Relevant transcript evidence is retrieved.



v



Dedicated Ship30 skill is applied.



v



Content is generated at approximately 1,250 words.



v



Output uses:



- Strong hook.

- Narrative structure.

- Skimmable headings.

- Bullets where useful.

- Selective emphasis.

- Useful takeaway.

- Grounded claims.



---



## 13. Artifact Flow



User requests an artifact.



v



Agent identifies artifact-generation task.



v



Relevant conversation/evidence is used.



v



Markdown or HTML/CSS is generated.



v



Generated HTML is treated as untrusted.



v



Content is sanitized and/or isolated according to the security design.



v



Artifact is rendered inside the application.



---



## 14. Functional Requirements



### FR-01 — Chat



The system must allow users to send product/growth questions and receive responses.



### FR-02 — Sessions



Each new conversation must have independent session context.



### FR-03 — Persistence



Sessions and messages must be persisted in PostgreSQL.



### FR-04 — Retrieval



The assistant must retrieve relevant Lenny transcript content before answering knowledge-based questions.



### FR-05 — Source Tracing



Answers should identify relevant transcript/source information.



### FR-06 — Grounding



The assistant must avoid presenting unsupported information as transcript-derived knowledge.



### FR-07 — Model Configuration



The application must support switching between a local Ollama provider and at least one cloud provider through configuration.



### FR-08 — Ship30 Skill



The application must provide a dedicated Ship30 writing skill.



### FR-09 — Artifact Generation



The assistant must generate Markdown or HTML/CSS artifacts.



### FR-10 — Artifact Viewer



Generated artifacts must be rendered natively inside the application.



### FR-11 — Security



Generated HTML must be handled as untrusted content.



### FR-12 — Health



The backend must expose health information sufficient to diagnose service availability.



### FR-13 — Errors



The API must validate requests and return structured errors.



### FR-14 — Logging



Important model, retrieval, database, and artifact failures must produce useful structured logs.



---



## 15. Acceptance Criteria



### Chat



- User can send a question.

- Assistant returns a response.

- Response is associated with the correct session.

- Relevant sources are shown when available.



### Sessions



- User can start a new conversation.

- New sessions do not inherit previous session context.

- Previous conversations can be retrieved.



### Grounding



- Relevant questions retrieve supporting transcript evidence.

- Unsupported questions produce an insufficient-evidence response.

- Assistant does not fabricate transcript claims.



### Model Switching



- Ollama can be selected.

- Cloud provider can be selected.

- Selected provider is visible in the UI or configuration.

- Missing credentials/unavailable provider produces a clear error.



### Ship30



- User can request Ship30-style content.

- Dedicated skill is used.

- Output is approximately 1,250 words.

- Output contains a strong hook and skimmable structure.

- Claims are grounded in retrieved evidence.



### Artifacts



- User can request an artifact.

- Markdown or HTML/CSS can be generated.

- Artifact is rendered in the Artifact Viewer.

- Untrusted HTML is isolated/sanitized according to the security design.



---



## 16. Risks and Mitigations



| Risk | Impact | Mitigation |

|---|---|---|

| Hallucination | High | Retrieval, source tracing, insufficient-evidence behavior |

| Poor retrieval | High | Retrieval evaluation tests and inspection |

| Ollama unavailable | High | Health checks and clear failure handling |

| Local model quality | Medium | Select a suitable model and document trade-offs |

| LLM latency | Medium | Timeouts and structured logging |

| Cloud API cost | Medium | Ollama available for local demonstration |

| Data leakage | High | Environment secrets, controlled external calls, safe logging |

| Unsafe HTML | High | Sanitization and/or sandboxed rendering |

| Database failure | High | Connection handling and structured errors |

| AI-generated defects | Medium | Automated tests, inspection, and manual verification |



---



## 17. Non-Functional Requirements



### Reliability



The application should fail gracefully when dependencies are unavailable.



### Security



Secrets must never be committed to the repository.



Generated HTML must be treated as untrusted.



### Maintainability



Backend, agent, retrieval, model providers, and frontend responsibilities should remain separated.



### Reproducibility



A fresh evaluator should be able to run the project using the documented setup.



### Observability



Logs should provide enough information to diagnose failures without exposing secrets.



---



## 18. Implementation Plan



1\. Repository and development foundation.

2\. FastAPI backend foundation.

3\. PostgreSQL persistence.

4\. Transcript ingestion.

5\. Retrieval/RAG.

6\. Agent architecture.

7\. Ollama and cloud model providers.

8\. Conversational chat.

9\. Ship30 skill.

10\. Artifact generation and viewer.

11\. Security and resilience.

12\. Automated testing.

13\. Documentation and handoff.

14\. Final evaluator verification.

15\. Demo and submission.



---



## 19. Development Discipline



For every meaningful feature:



### Before Coding



**Understand -> Decide -> Implement**



### After Coding



**Run -> Test -> Inspect -> Fix**



### Before Pushing



**Verify -> Commit -> Push**



No feature is considered complete until it has been tested and inspected.



---



## 20. Definition of Done



The project is considered ready for submission when:



- Core chat flow works.

- Sessions are isolated and persisted.

- Lenny transcript retrieval works.

- Answers are grounded and source-traceable.

- Unsupported questions are handled safely.

- Ollama works locally.

- Cloud model works.

- Model provider can be configured.

- Ship30 skill works.

- Artifacts render inside the application.

- HTML rendering is reasonably isolated/sanitized.

- Critical tests pass.

- Errors are handled gracefully.

- Logs support troubleshooting.

- Docker/local startup is documented.

- README, PRD, design, and architecture documentation are complete.

- Agent transcripts are included and scrubbed.

- Fresh-clone verification succeeds.

- Demo video is prepared.



---



## 21. Open Technical Decisions



The following decisions will be finalized during implementation:



- Anthropic Claude Agent SDK vs Pi Coding Agent.

- Exact cloud LLM provider.

- Exact Ollama model.

- Embedding model.

- Exact chunking strategy.

- PostgreSQL/pgvector deployment approach.

- HTML sanitization/sandbox strategy.

- Frontend component/library choices.

- Docker service topology.

