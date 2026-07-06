"""Tests for scripts/time_utils.py — utilidades de timezone Argentina."""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from time_utils import TZ_AR, now_ar, today_ar, now_ar_iso, parse_ts, hours_since


class TestTodayAr:
    def test_returns_yyyy_mm_dd_format(self):
        result = today_ar()
        assert len(result) == 10
        datetime.strptime(result, "%Y-%m-%d")  # no debe lanzar

    def test_matches_now_ar_date(self):
        assert today_ar() == now_ar().strftime("%Y-%m-%d")


class TestNowAr:
    def test_is_aware_with_ar_offset(self):
        dt = now_ar()
        assert dt.tzinfo is not None
        assert dt.utcoffset() is not None


class TestNowArIso:
    def test_has_offset_suffix(self):
        result = now_ar_iso()
        # Offset AR: -03:00 (sin horario de verano actualmente)
        assert result[-6:] in ("-03:00", "-02:00")  # tolerante a cambios históricos de DST


class TestParseTs:
    def test_naive_string_assumed_ar(self):
        result = parse_ts("2026-03-25T10:00:00")
        assert result.tzinfo is not None
        assert result.utcoffset() == TZ_AR.utcoffset(result)

    def test_aware_string_preserves_offset(self):
        result = parse_ts("2026-07-02T10:00:00-03:00")
        assert result.tzinfo is not None
        assert result.utcoffset().total_seconds() == -3 * 3600

    def test_aware_string_utc_preserves_offset(self):
        result = parse_ts("2026-07-02T13:00:00+00:00")
        assert result.utcoffset().total_seconds() == 0


class TestHoursSince:
    def test_naive_timestamp_does_not_raise(self):
        # No debe lanzar TypeError al restar aware - naive
        past = (now_ar().replace(tzinfo=None)).isoformat()
        result = hours_since(past)
        assert isinstance(result, float)

    def test_past_timestamp_gives_positive_value(self):
        past_iso = "2020-01-01T00:00:00"
        result = hours_since(past_iso)
        assert result > 0

    def test_aware_past_timestamp_gives_positive_value(self):
        past_iso = "2020-01-01T00:00:00-03:00"
        result = hours_since(past_iso)
        assert result > 0


class TestUtcToArDateBoundary:
    """Caso borde: 02:30 UTC == 23:30 AR del día anterior."""

    def test_date_differs_across_midnight_boundary(self):
        utc_instant = datetime(2026, 7, 2, 2, 30, tzinfo=timezone.utc)
        ar_instant = utc_instant.astimezone(TZ_AR)

        assert ar_instant.date() != utc_instant.date()
        assert ar_instant.date().isoformat() == "2026-07-01"
        assert utc_instant.date().isoformat() == "2026-07-02"
        assert ar_instant.hour == 23
        assert ar_instant.minute == 30
