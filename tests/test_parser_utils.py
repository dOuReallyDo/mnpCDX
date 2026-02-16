from datetime import date

from mnp_cdx.ingest.parser import MNPParser


def test_daily_date_rollover() -> None:
    parser = MNPParser()
    header = ("31/12", "1/1", "2/1")
    mapping = parser._map_daily_columns(header, 2025)
    assert mapping[0] == date(2025, 12, 31)
    assert mapping[1] == date(2026, 1, 1)


def test_monthly_map_with_compact_and_short() -> None:
    parser = MNPParser()
    header = ("Jan 23", "Feb", "Mar", "Apr 24")
    mapping = parser._map_monthly_columns(header)
    assert mapping[0] == date(2023, 1, 1)
    assert mapping[1] == date(2023, 2, 1)
    assert mapping[3] == date(2024, 4, 1)
