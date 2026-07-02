#!/usr/bin/env python3
"""
Cliente LLM compartido para InforMessi (Groq).

Extraído de generate-message.py (call_llm_groq) para ser reusado por el
generador y por el sistema de evals (judge LLM).
"""

import logging
import os
import sys
import time

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_groq(prompt, model="llama-3.1-8b-instant", temperature=0.7, max_tokens=300,
              json_mode=False, system=None):
    """Llama a Groq API (gratuita) para generar texto, con retry en rate limit.

    - json_mode=True agrega response_format={"type": "json_object"} al payload.
    - system, si se pasa, se agrega como mensaje "system" antes del user.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        logger.error("ERROR: GROQ_API_KEY no configurada")
        sys.exit(1)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    max_retries = 5
    for attempt in range(max_retries):
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", 15))
            wait = max(retry_after, 10 * (attempt + 1))
            logger.warning(f"⏳ Rate limit Groq, esperando {wait}s (intento {attempt + 1}/{max_retries})...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    response.raise_for_status()  # último intento, dejar que falle
