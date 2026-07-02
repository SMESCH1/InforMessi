"""Tests for fetch-weather.py core functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from importlib import import_module

fw = import_module("fetch-weather")

get_weather = fw.get_weather
format_weather_block = fw.format_weather_block


def _mock_response(payload, status_code=200, raise_for_status_error=None):
    class _Resp:
        def __init__(self):
            self.status_code = status_code

        def json(self):
            return payload

        def raise_for_status(self):
            if raise_for_status_error:
                raise raise_for_status_error

    return _Resp()


class TestFormatWeatherBlock:
    def test_basic_block(self):
        weather = {
            "amba": {"min": 8, "max": 17},
            "la_plata": {"min": 6, "max": 16},
            "fetched_at": "2026-07-02T08:00:00-03:00",
            "source": "open-meteo",
        }
        block = format_weather_block(weather)
        lines = block.strip().split("\n")

        assert "🌤" in block
        assert "Clima" in lines[0]
        assert "AMBA: min 8° / max 17°" in block
        assert "La Plata: min 6° / max 16°" in block
        assert "smn.gob.ar/pronostico" in block

    def test_negative_temperatures(self):
        weather = {
            "amba": {"min": -2, "max": 10},
            "la_plata": {"min": -4, "max": 9},
            "fetched_at": "2026-07-02T08:00:00-03:00",
            "source": "open-meteo",
        }
        block = format_weather_block(weather)
        assert "AMBA: min -2° / max 10°" in block
        assert "La Plata: min -4° / max 9°" in block


class TestGetWeather:
    def test_parses_min_max_and_rounds(self, monkeypatch):
        calls = []

        def fake_get(url, params=None, timeout=None):
            calls.append(params)
            lat = params.get("latitude")
            if lat == -34.61:
                payload = {
                    "daily": {
                        "time": ["2026-07-02"],
                        "temperature_2m_min": [7.6],
                        "temperature_2m_max": [16.4],
                    }
                }
            else:
                payload = {
                    "daily": {
                        "time": ["2026-07-02"],
                        "temperature_2m_min": [5.5],
                        "temperature_2m_max": [15.5],
                    }
                }
            return _mock_response(payload)

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is not None
        assert result["amba"] == {"min": 8, "max": 16}
        assert result["la_plata"] == {"min": 6, "max": 16}  # round-half-to-even: 5.5 -> 6, 15.5 -> 16
        assert result["source"] == "open-meteo"
        assert "fetched_at" in result
        assert len(calls) == 2

    def test_network_error_returns_none(self, monkeypatch):
        import requests

        def fake_get(url, params=None, timeout=None):
            raise requests.exceptions.ConnectionError("boom")

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is None

    def test_http_error_returns_none(self, monkeypatch):
        import requests

        def fake_get(url, params=None, timeout=None):
            return _mock_response(
                {}, status_code=500,
                raise_for_status_error=requests.exceptions.HTTPError("server error"),
            )

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is None

    def test_empty_response_returns_none(self, monkeypatch):
        def fake_get(url, params=None, timeout=None):
            return _mock_response({})

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is None

    def test_missing_daily_data_returns_none(self, monkeypatch):
        def fake_get(url, params=None, timeout=None):
            payload = {"daily": {"time": [], "temperature_2m_min": [], "temperature_2m_max": []}}
            return _mock_response(payload)

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is None

    def test_unexpected_exception_returns_none(self, monkeypatch):
        def fake_get(url, params=None, timeout=None):
            raise ValueError("unexpected")

        monkeypatch.setattr(fw.requests, "get", fake_get)

        result = fw.get_weather("2026-07-02")

        assert result is None
