# Lenny Growth Assistant - Product & UX Design

## 1. Design Principles

### Grounded by Default

The assistant should answer product and growth questions using evidence retrieved from the Lenny transcript knowledge base. It must not present unsupported information as transcript-derived knowledge.

### Evidence Before Confidence

When retrieval does not provide sufficient evidence, the assistant should clearly communicate the limitation rather than fabricate an answer.

### Simple for the User

Users should interact through normal conversation. They should not need to understand RAG, embeddings, agents, model providers, or infrastructure.

### Transparent Sources

When an answer is based on transcript evidence, relevant source information should be visible so users can inspect where the answer came from.

### Independent Conversations

Each conversation is an independent session. Starting a new conversation must not inherit context from another session.

---

## 2. Primary User Experience

The primary experience is a conversational workspace for product and growth professionals.

The user should be able to:

1. Start a new conversation.
2. Ask a product or growth question.
3. Receive a grounded answer.
4. Inspect relevant sources.
5. Ask follow-up questions.
6. Generate Ship30-style written content.
7. Generate Markdown or HTML/CSS artifacts.
8. Continue working without manually managing prompts or model configuration.

---

## 3. Chat Experience

The interface should contain:

- Conversation/session navigation.
- Main chat area.
- Message composer.
- Assistant responses.
- Source references where evidence is available.
- Artifact Viewer when an artifact is generated.

A new conversation creates a new session identifier.

Messages must remain associated with their session.

---

## 4. Grounded Answer Experience

For a knowledge-based question:

User question
-> retrieve relevant transcript evidence
-> evaluate evidence
-> generate grounded answer
-> display sources

The assistant should prioritize useful synthesis over simply returning transcript excerpts.

The response should distinguish between:

- Information supported by retrieved evidence.
- Reasonable synthesis of retrieved evidence.
- Information that cannot be supported by the knowledge base.

The assistant must not imply that unsupported information came from Lenny.

---

## 5. Insufficient Evidence Experience

When retrieval does not provide sufficient evidence:

User question
-> retrieval
-> insufficient evidence
-> transparent limitation response

The assistant should say that sufficient supporting information was not found in the Lenny knowledge base.

It should not invent:

- Quotes.
- Speaker opinions.
- Episode references.
- Transcript claims.
- Sources.

The failure should still feel useful where possible, for example by suggesting that the user rephrase the question.

---

## 6. Follow-Up Experience

Follow-up questions should use the current session context.

Example:

User:
"What are the main activation principles?"

Assistant:
Grounded answer.

User:
"Which of those would you prioritize for a B2B product?"

The assistant should understand that "those" refers to the previous answer while still retrieving relevant transcript evidence for the follow-up.

A new session must not inherit this context.

---

## 7. Source Experience

Sources should provide enough information to identify the supporting transcript material.

Source metadata may include:

- Episode title.
- Speaker.
- Transcript location or timestamp when available.
- Relevant excerpt.
- Source identifier or URL when available.

The source representation should help the user verify the answer without overwhelming the main conversation.

---

## 8. Ship30 Experience

The user can request reusable written content from the current discussion.

The Ship30 flow should:

1. Identify the writing task.
2. Retrieve relevant transcript evidence.
3. Apply the dedicated Ship30 writing skill.
4. Produce approximately 1,250 words.
5. Use a strong hook.
6. Maintain a clear narrative.
7. Use skimmable headings.
8. Use bullets where useful.
9. Use selective emphasis.
10. End with a useful takeaway.
11. Keep substantive claims grounded in available evidence.

The generated content should be presented as a distinct piece of content rather than being mixed into ordinary conversational text.

---

## 9. Artifact Experience

The user can request a visual or structured artifact based on the conversation.

Supported initial formats:

- Markdown.
- HTML/CSS.

Example:

"Create a product-growth framework based on this discussion."

The system should:

1. Identify the artifact task.
2. Use relevant conversation context and transcript evidence.
3. Generate the requested artifact.
4. Treat generated HTML as untrusted.
5. Sanitize and/or isolate the HTML according to the security design.
6. Render the result in the Artifact Viewer.

---

## 10. Artifact Viewer

The Artifact Viewer should appear alongside or adjacent to the conversation when an artifact is available.

The viewer should:

- Render supported artifact output.
- Make the generated result easy to inspect.
- Preserve the conversation as the primary workspace.
- Clearly distinguish generated artifacts from ordinary assistant messages.

The initial implementation should favor reliability and safe rendering over a large set of editing features.

---

## 11. Model Provider Experience

The application supports:

- Local Ollama.
- At least one cloud LLM provider.

Provider selection should be configuration-driven rather than requiring application-code changes.

The selected provider should be visible through configuration and/or the UI where useful.

If a provider is unavailable or credentials are missing, the user should receive a clear actionable error.

The system should not expose API keys or secrets in the interface or logs.

---

## 12. Loading and Error States

The interface should clearly communicate:

- Request in progress.
- Retrieval in progress where useful.
- Provider unavailable.
- Missing credentials.
- Database unavailable.
- Empty retrieval results.
- Artifact generation failure.
- Invalid request.

Errors should be understandable to users while detailed diagnostic information remains available through structured logs.

---

## 13. Security UX

Generated HTML is untrusted.

The product should not allow generated content to compromise the host application.

The implementation will use sanitization and/or isolation appropriate to the chosen rendering approach.

Secrets must never be displayed in:

- Chat responses.
- Artifacts.
- Logs.
- Source references.

---

## 14. Accessibility and Usability

The interface should provide:

- Clear visual hierarchy.
- Keyboard-accessible interaction.
- Readable typography.
- Clear loading and error states.
- Meaningful labels for controls.
- Responsive layout for practical desktop use.

The primary evaluation target is desktop because the assignment is a full-stack web application rather than a mobile application.

---

## 15. UX Scope Decisions

### Included

- Conversational chat.
- Independent sessions.
- Source references.
- Follow-up questions.
- Ship30 generation.
- Artifact generation.
- Artifact viewing.
- Provider visibility.
- Useful error states.

### Excluded from MVP

- Enterprise SSO.
- Billing.
- Mobile-specific application.
- Complex administration.
- Advanced analytics.
- Multi-tenant enterprise permissions.
- Large-scale artifact editing.

These exclusions keep the implementation focused on the assignment's core evaluation areas.

---

## 16. UX Success Criteria

The UX is successful when an evaluator can:

- Start a conversation without special instructions.
- Ask a product/growth question.
- Understand the grounded answer.
- Inspect supporting sources.
- Ask a meaningful follow-up.
- Start another independent conversation.
- Request Ship30-style content.
- Request an artifact.
- View the generated artifact.
- Understand provider or dependency failures.
- Complete the core workflow without understanding the underlying architecture.

---

## 17. Design Principle for Implementation

The interface should expose the value of the underlying system without exposing unnecessary implementation complexity.

The user sees:

Conversation -> Evidence -> Answer -> Sources -> Artifact

The system internally handles:

Agent -> Retrieval -> BM25 + pgvector -> Ranking -> LLM -> Persistence
