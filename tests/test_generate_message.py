"""Tests for generate-message.py core functions."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from importlib import import_module

gm = import_module("generate-message")

calculate_days_remaining = gm.calculate_days_remaining
_extract_json = gm._extract_json
parse_selection_response = gm.parse_selection_response
_fallback_selection = gm._fallback_selection
_format_event_for_selection = gm._format_event_for_selection
_format_event_for_prompt = gm._format_event_for_prompt
_format_news_for_prompt = gm._format_news_for_prompt


class TestDaysRemaining:
    def test_basic(self):
        assert calculate_days_remaining("2026-06-11", "2026-06-01") == 10

    def test_same_day(self):
        assert calculate_days_remaining("2026-06-11", "2026-06-11") == 0

    def test_past(self):
        assert calculate_days_remaining("2026-06-11", "2026-06-12") == -1

    def test_full_range(self):
        assert calculate_days_remaining("2026-06-11", "2026-01-01") == 161


class TestExtractJson:
    def test_clean_json(self):
        text = '{"selected_event_ids": ["E1"], "selected_news_ids": ["N2"]}'
        assert _extract_json(text) == text

    def test_json_with_surrounding_text(self):
        text = 'Here is my answer: {"a": 1} hope that helps'
        assert _extract_json(text) == '{"a": 1}'

    def test_no_json(self):
        assert _extract_json("no json here") == ""

    def test_only_open_brace(self):
        assert _extract_json("{ incomplete") == ""

    def test_nested_braces(self):
        text = '{"outer": {"inner": 1}}'
        assert _extract_json(text) == text


class TestParseSelectionResponse:
    EVENTS = [
        {"type": "birthday", "person": "Messi", "description": "Cumple"},
        {"type": "match", "description": "Argentina vs Brasil"},
    ]
    NEWS = [
        {"title": "Noticia A"},
        {"title": "Noticia B"},
        {"title": "Noticia C"},
    ]

    def test_valid_selection(self):
        response = '{"selected_event_ids": ["E1"], "selected_news_ids": ["N2", "N3"]}'
        events, news = parse_selection_response(response, self.EVENTS, self.NEWS)
        assert len(events) == 1
        assert events[0]["person"] == "Messi"
        assert len(news) == 2
        assert news[0]["title"] == "Noticia B"
        assert news[1]["title"] == "Noticia C"

    def test_garbage_response_uses_fallback(self):
        events, news = parse_selection_response("garbage", self.EVENTS, self.NEWS)
        assert len(events) == 1
        assert len(news) == 2

    def test_empty_selection_uses_fallback(self):
        response = '{"selected_event_ids": [], "selected_news_ids": []}'
        events, news = parse_selection_response(response, self.EVENTS, self.NEWS)
        assert len(events) == 1  # fallback picks first

    def test_out_of_range_id_ignored(self):
        response = '{"selected_event_ids": ["E99"], "selected_news_ids": ["N1"]}'
        events, news = parse_selection_response(response, self.EVENTS, self.NEWS)
        assert len(events) == 0
        assert len(news) == 1

    def test_invalid_id_format_ignored(self):
        response = '{"selected_event_ids": ["X1"], "selected_news_ids": ["N1"]}'
        events, news = parse_selection_response(response, self.EVENTS, self.NEWS)
        assert len(events) == 0
        assert len(news) == 1


class TestFallbackSelection:
    def test_with_data(self):
        events = [{"a": 1}, {"b": 2}]
        news = [{"c": 3}, {"d": 4}, {"e": 5}]
        sel_events, sel_news = _fallback_selection(events, news)
        assert sel_events == [{"a": 1}]
        assert sel_news == [{"c": 3}, {"d": 4}]

    def test_empty(self):
        sel_events, sel_news = _fallback_selection([], [])
        assert sel_events == []
        assert sel_news == []


class TestFormatEvent:
    def test_birthday_selection(self):
        event = {"type": "birthday", "person": "Messi", "age": 39, "description": "Cumple"}
        result = _format_event_for_selection(event)
        assert "Messi" in result
        assert "39" in result

    def test_match_selection(self):
        event = {"type": "match", "opponent": "Brasil", "venue": "Monumental", "time": "21:00", "description": "Amistoso"}
        result = _format_event_for_selection(event)
        assert "Brasil" in result
        assert "Monumental" in result

    def test_generic_event(self):
        event = {"description": "Evento generico"}
        assert _format_event_for_selection(event) == "Evento generico"

    def test_birthday_prompt(self):
        event = {"type": "birthday", "person": "Di Maria", "age": 38, "description": "Cumple"}
        result = _format_event_for_prompt(event)
        assert "Di Maria" in result
        assert "38" in result
        assert result.startswith("- ")


class TestFormatNews:
    def test_with_description(self):
        news = {"title": "Titulo", "description": "Desc larga", "source": "TyC"}
        result = _format_news_for_prompt(news)
        assert "Titulo" in result
        assert "Desc larga" in result
        assert "TyC" in result

    def test_without_description(self):
        news = {"title": "Solo titulo", "source": "ESPN"}
        result = _format_news_for_prompt(news)
        assert "Solo titulo" in result
        assert "ESPN" in result
