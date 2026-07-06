#!/usr/bin/env python3
"""
Utilidades de normalización de texto para InforMessi.

Centraliza la lógica de normalización usada por varios módulos del
pipeline (fetch-news.py, scrape-daily-news.py, rag_memory_database.py)
para evitar reimplementaciones divergentes.
"""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normaliza texto: minúsculas, sin acentos/diacríticos, espacios
    colapsados. NO quita puntuación (ej. "años", "¡hola!" conservan sus
    signos no diacríticos). Usado para matching de keywords/blacklist
    (fetch-news.py) y para las claves de memoria persistente
    (rag_memory_database.py), donde no hace falta ni conviene tocar la
    puntuación."""
    text = (text or "").lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_title_for_dedupe(title: str) -> str:
    """Normaliza un título para comparación de dedupe: además de
    `normalize_text`, quita signos de puntuación. Usado en
    scrape-daily-news.py para que distinta puntuación entre fuentes
    (ej. "¡...!" vs sin signos) no impida detectar duplicados exactos."""
    text = normalize_text(title)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
