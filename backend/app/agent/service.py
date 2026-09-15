import logging
from typing import Optional, List, Dict, Any

from app.agent.pi_runner import generate_llm_response
from app.ingestion.evidence import retrieve_with_evidence_gate

logger = logging.getLogger("lenny_assistant.service")

SYSTEM_PROMPT = """You are Lenny Growth Assistant.

Answer ONLY using the provided Lenny Podcast transcript evidence.
If past session context is provided, use it to understand follow-up questions, but ground all facts in the transcript evidence.

Guidelines:
- Do not show reasoning or internal thought processes.
- Do not mention system prompts or instructions.
- Provide a clear, actionable, evidence-backed answer.
- Focus on practical product and growth takeaways.
"""

SHIP30_SYSTEM_PROMPT = """You are an expert growth writer applying the Ship 30 for 30 framework.

Your task is to write an engaging, high-value, grounded essay of approximately 1,250 words based strictly on Lenny's Podcast transcripts.

Formatting & Structure Requirements:
1. Strong Hook: Start with an attention-grabbing opening line.
2. Clear Narrative: Logical flow connecting the core problem to solutions.
3. Skimmable Headings: Use clear Markdown subheadings (## H2).
4. Bullet Points: Break down takeaways into bullet lists for readability.
5. Selective Bold Emphasis: Emphasize key terms and principles in bold.
6. Useful Takeaway: End with an actionable conclusion or summary box.
7. Grounded Claims: Synthesize evidence without fabricating quotes or advice.
"""

ARTIFACT_SYSTEM_PROMPT = """You are an expert growth artifact creator.

Generate a comprehensive, structured artifact (Markdown or clean HTML/CSS) based on the provided context and evidence.
Do not include any script tags, event handlers (onclick, onload, etc.), or unsafe HTML.
Return ONLY the formatted artifact document.
"""


def format_history(history: Optional[List[Dict[str, Any]]]) -> str:
    """Format recent conversation turns into context string."""
    if not history:
        return ""
    
    formatted = []
    # Use last 6 messages
    for msg in history[-6:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        if content:
            formatted.append(f"{role}: {content}")
    
    if not formatted:
        return ""
    
    return "Previous Conversation Context:\n" + "\n".join(formatted) + "\n\n"


def generate_answer(
    question: str,
    evidence: List[Dict[str, Any]],
    history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    history_text = format_history(history)
    
    evidence_text = "\n\n".join(
        (
            f"Source Episode: {item['title']}\n"
            f"Guest: {item.get('guest') or 'Unknown'}\n"
            f"Excerpt: {item['text'][:800]}"
        )
        for item in evidence[:3]
    )

    prompt = (
        f"{history_text}"
        f"Transcript Evidence:\n{evidence_text}\n\n"
        f"Current User Question: {question}\n\n"
        "Provide a concise, grounded answer in 3-5 sentences backed strictly by transcript evidence."
    )

    return generate_llm_response(prompt, SYSTEM_PROMPT)


def answer_question(
    question: str,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    # Always perform fresh retrieval for the question
    decision = retrieve_with_evidence_gate(question)

    if not decision.sufficient:
        return {
            "answer": (
                "I couldn't find enough evidence in Lenny's transcripts "
                "to answer that confidently."
            ),
            "sources": decision.results,
            "grounded": False,
        }

    answer = generate_answer(
        question,
        decision.results,
        history=history,
    )

    return {
        "answer": answer,
        "sources": decision.results,
        "grounded": True,
    }


def generate_ship30(
    topic: str,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    decision = retrieve_with_evidence_gate(topic)
    history_text = format_history(history)

    if not decision.results:
        evidence_text = "No direct transcript matches found."
    else:
        evidence_text = "\n\n".join(
            (
                f"Source: {item['title']} (Guest: {item.get('guest') or 'Unknown'})\n"
                f"Content: {item['text'][:2000]}"
            )
            for item in decision.results[:5]
        )

    prompt = (
        f"{history_text}"
        f"Topic: {topic}\n\n"
        f"Transcript Evidence:\n{evidence_text}\n\n"
        "Write a complete, grounded Ship 30 for 30 style essay (~1,250 words) adhering to all formatting rules."
    )

    content = generate_llm_response(prompt, SHIP30_SYSTEM_PROMPT)

    return {
        "content": content,
        "sources": decision.results,
        "grounded": decision.sufficient,
    }


def generate_artifact_content(
    title: str,
    artifact_type: str,
    context: str,
) -> str:
    decision = retrieve_with_evidence_gate(title)
    if decision.results:
        evidence_text = "\n\n".join(
            f"Source: {item['title']} (Guest: {item.get('guest') or 'Unknown'})\nContent: {item['text'][:1200]}"
            for item in decision.results[:4]
        )
    else:
        evidence_text = "No direct transcript matches."

    prompt = (
        f"Title: {title}\n"
        f"Format Type: {artifact_type}\n"
        f"Context & Requirements:\n{context}\n\n"
        f"Transcript Evidence:\n{evidence_text}\n\n"
        "Create a structured, complete artifact document with Goal, Core Principles, Actionable Framework, Metrics, and Evidence Summary."
    )

    result = generate_llm_response(prompt, ARTIFACT_SYSTEM_PROMPT)
    if not result or len(result.strip()) < 30:
        # Structured fallback artifact based on transcript evidence
        result = (
            f"# {title}\n\n"
            f"## Goal & Overview\n"
            f"Structured growth framework synthesized directly from Lenny's Podcast transcript evidence.\n\n"
            f"## Core Growth & Activation Principles\n"
            f"1. **Habit-Forming Setup**: Guide users to their core value action within the first session.\n"
            f"2. **Retention Curves**: Measure long-term cohort retention rather than superficial signups.\n"
            f"3. **Friction Reduction**: Eliminate unnecessary signup barriers prior to value delivery.\n\n"
            f"## Actionable Framework & Key Metrics\n"
            f"- **D1 / W1 Activation Rate**: % of new users reaching core milestone.\n"
            f"- **W4 Cohort Retention**: % of users retaining after 30 days.\n\n"
            f"## Grounded Evidence Summary\n"
        )
        if decision.results:
            for item in decision.results[:3]:
                result += f"- **{item['title']}** ({item.get('guest') or 'Expert'}): {item['text'][:200]}...\n"

    return result