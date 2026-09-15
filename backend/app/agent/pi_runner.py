import json
import logging
import os
import re
import shutil
import subprocess
import urllib.request
from typing import Optional

from app.config.settings import settings

logger = logging.getLogger("lenny_assistant.agent")


def strip_reasoning(text: str) -> str:
    """Strip reasoning/thinking blocks like <think>...</think> from output."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def run_pi_agent(prompt: str, system_prompt: str, timeout: int = 15) -> Optional[str]:
    """
    Executes Pi Coding Agent via CLI (pi / pi.cmd / npx @mariozechner/pi-coding-agent).
    Returns response string if successful, or None if unavailable/failed.
    """
    pi_bin = shutil.which("pi") or shutil.which("pi.cmd")
    cmd = []
    
    if pi_bin:
        cmd = [pi_bin]
    else:
        cmd = ["npx.cmd" if os.name == "nt" else "npx", "--yes", "@mariozechner/pi-coding-agent"]

    provider = settings.llm_provider.lower()
    if provider == "ollama":
        model_arg = f"ollama/{settings.ollama_model}"
    elif provider == "anthropic":
        model_arg = f"anthropic/{settings.anthropic_model}"
    elif provider == "openai":
        model_arg = f"openai/{settings.openai_model}"
    else:
        model_arg = settings.ollama_model

    cmd.extend([
        "--mode", "text",
        "--model", model_arg,
        "--thinking", "off",
        "--no-tools",
        "--system-prompt", system_prompt,
        "-p", prompt,
    ])

    env = os.environ.copy()
    if settings.anthropic_api_key:
        env["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    if settings.openai_api_key:
        env["OPENAI_API_KEY"] = settings.openai_api_key

    try:
        logger.info(f"Running Pi Agent command: {' '.join(cmd[:6])}...")
        result = subprocess.run(
            cmd,
            input="",
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("Pi Agent execution succeeded")
            return strip_reasoning(result.stdout)
        else:
            logger.warning(f"Pi Agent non-zero exit or empty stdout: {result.stderr[:200]}")
    except Exception as e:
        logger.warning(f"Pi Agent execution failed/timed out: {e}")

    return None


def run_ollama_direct(prompt: str, system_prompt: str) -> str:
    """Direct low-latency call to Ollama REST API with think: false."""
    base_url = settings.ollama_base_url.rstrip("/")
    url = f"{base_url}/api/chat"
    
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "num_predict": 600,
            "temperature": 0.2,
            "think": False,
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            message_content = data.get("message", {}).get("content", "")
            return strip_reasoning(message_content)
    except Exception as e:
        logger.error(f"Ollama connection error: {e}")
        raise RuntimeError(f"OLLAMA_UNAVAILABLE: Failed to connect to Ollama at {base_url}: {e}")


def run_anthropic_direct(prompt: str, system_prompt: str) -> str:
    """Direct call to Anthropic API if key is present."""
    if not settings.anthropic_api_key:
        raise ValueError("LLM_UNAVAILABLE: Anthropic API key is not configured.")

    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": settings.anthropic_model,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content_list = data.get("content", [])
            if content_list and "text" in content_list[0]:
                return strip_reasoning(content_list[0]["text"])
            return ""
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"LLM_UNAVAILABLE: Anthropic API returned HTTP {e.code}: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"LLM_UNAVAILABLE: Anthropic request failed: {e}")


def generate_llm_response(prompt: str, system_prompt: str) -> str:
    """
    Primary agent entrypoint:
    Attempts Pi Coding Agent CLI runner first.
    Falls back cleanly to direct provider API if needed.
    """
    provider = settings.llm_provider.lower()

    # If Anthropic provider requested but no key configured:
    if provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("LLM_UNAVAILABLE: Anthropic API key is missing. Configure ANTHROPIC_API_KEY or set LLM_PROVIDER=ollama.")

    # Try Pi Agent runtime first
    pi_output = run_pi_agent(prompt, system_prompt)
    if pi_output:
        return pi_output

    # Fallback to direct provider connection
    logger.info(f"Falling back to direct provider API for '{provider}'")
    if provider == "anthropic":
        return run_anthropic_direct(prompt, system_prompt)
    else:
        return run_ollama_direct(prompt, system_prompt)
