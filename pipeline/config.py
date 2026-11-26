"""Shared settings: paths, years, station IDs. No logic here."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CLEAN = ROOT / "data" / "clean"

YEARS = list(range(2015, 2025))
PATTERN_YEARS = [2016, 2017, 2018, 2019, 2021, 2022] # training years only
CLARK = "E316370"
LOCAL_TZ = "America/Vancouver"

# Forecast hour (D1), scored rows (D6), New Year rule (D7) and training hours (D11) go here once decided.
