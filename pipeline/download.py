"""Download raw inputs into data/raw/. Downloads and saves only: no cleaning, no unit changes.

Design: SchoolObsidianVault/.../project_ds/02_data_sources.md, "Logic".
Standard library only, so it runs before the .venv exists.

Each source is a function that writes one file. To add a source, write one
function and add one entry to SOURCES.
"""

import csv
import datetime as dt
import io
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

BC_ARCHIVE = "ftp://ftp.env.gov.bc.ca/pub/outgoing/AIR/AnnualSummary"
ECCC_API = "https://api.weather.gc.ca/collections/climate-hourly/items"
LOWER_MAINLAND = "02 - Lower Mainland"
YVR_CLIMATE_ID = "1108395"
STATION_LIST_YEAR = 2024 # the station list is read from this year's folder

TRIES = 4
TIMEOUT = 120 # seconds per request


# ---------- helpers ----------

def _open(url):
    """Open a URL, retrying with a growing wait if it fails."""
    for attempt in range(1, TRIES + 1):
        try:
            return urllib.request.urlopen(url, timeout=TIMEOUT)
        except Exception as err: # network errors come in many types
            if attempt == TRIES:
                raise
            wait = 5 * attempt
            print(f"    retry {attempt}/{TRIES - 1} in {wait}s ({err})")
            time.sleep(wait)


def _finish(tmp, final):
    """Rename a finished temp file, so a stopped run never leaves a half file that looks done."""
    os.replace(tmp, final)
    return final


def _count_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1 # minus the header


# ---------- sources ----------

def bc_pollutant(param, region=LOWER_MAINLAND):
    """Source for one pollutant file from the BC archive, filtered to one region."""

    def fetch(year, out):
        url = f"{BC_ARCHIVE}/{year}/{param}.csv"
        tmp = out.with_suffix(".part")
        with _open(url) as resp, open(tmp, "w", newline="", encoding="utf-8") as f:
            reader = csv.reader(io.TextIOWrapper(resp, encoding="utf-8-sig", newline=""))
            header = next(reader)
            if "REGION" not in header:
                raise ValueError(f"{url}: no REGION column; header is {header}")
            col = header.index("REGION")
            writer = csv.writer(f)
            writer.writerow(header)
            for row in reader:
                if len(row) > col and row[col] == region:
                    writer.writerow(row)
        return url, _finish(tmp, out)

    return fetch


def bc_station_list(year, out):
    """The BC station list (one file, not per year)."""
    url = f"{BC_ARCHIVE}/{STATION_LIST_YEAR}/bc_air_monitoring_stations.csv"
    tmp = out.with_suffix(".part")
    with _open(url) as resp, open(tmp, "wb") as f:
        f.write(resp.read())
    return url, _finish(tmp, out)


def eccc_hourly(climate_id):
    """Source for one ECCC weather station: 12 monthly requests, joined into one year file."""

    def fetch(year, out):
        rows = []
        for month in range(1, 13):
            offset = 0
            while True: # a month is under 1000 rows, but page anyway in case
                query = urllib.parse.urlencode({
                    "CLIMATE_IDENTIFIER": climate_id,
                    "LOCAL_YEAR": year,
                    "LOCAL_MONTH": month,
                    "limit": 1000,
                    "offset": offset,
                    "f": "json",
                })
                with _open(f"{ECCC_API}?{query}") as resp:
                    page = json.load(resp)
                feats = page.get("features", [])
                rows += [feat["properties"] for feat in feats]
                offset += len(feats)
                if not feats or offset >= page.get("numberMatched", 0):
                    break
        if not rows:
            raise ValueError(f"climate ID {climate_id}: no rows for {year}")
        cols = list(dict.fromkeys(k for r in rows for k in r)) # every field, first-seen order
        tmp = out.with_suffix(".part")
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)
        return f"{ECCC_API}?CLIMATE_IDENTIFIER={climate_id}", _finish(tmp, out)

    return fetch


# name -> (folder, file name pattern, per year?, function)
SOURCES = {
    "no2": ("no2", "{year}.csv", True, bc_pollutant("NO2")),
    "stations": ("stations", "bc_air_monitoring_stations.csv", False, bc_station_list),
    "weather": ("weather_yvr", "{year}.csv", True, eccc_hourly(YVR_CLIMATE_ID)),
}


# ---------- runner ----------

def planned_files(raw_dir, names, years):
    """Every (source, year, path) the given sources and years would produce."""
    out = []
    for name in names:
        folder, pattern, per_year, _ = SOURCES[name]
        for year in (years if per_year else [None]):
            out.append((name, year, Path(raw_dir) / folder / pattern.format(year=year)))
    return out


def _update_manifest(raw_dir, entries):
    """One line per file: what it is, where it came from, when, how big. Keeps the newest line per file."""
    path = Path(raw_dir) / "manifest.csv"
    fields = ["file", "source_url", "downloaded_utc", "bytes", "rows"]
    old = {}
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            old = {r["file"]: r for r in csv.DictReader(f)}
    old.update({e["file"]: e for e in entries})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(old[k] for k in sorted(old))


def download(raw_dir, names, years, force=False):
    """Download what's missing (or everything, with force). Returns the files that failed."""
    raw_dir = Path(raw_dir)
    done, failed = [], []
    for name, year, path in planned_files(raw_dir, names, years):
        label = path.relative_to(raw_dir)
        if path.exists() and not force:
            print(f"  skip  {label} (already there)")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"  get   {label} ...", flush=True)
        start = time.time()
        try:
            url, _ = SOURCES[name][3](year, path)
        except Exception as err:
            print(f"  FAIL  {label}: {err}")
            path.with_suffix(".part").unlink(missing_ok=True)
            failed.append(str(label))
            continue
        rows = _count_rows(path)
        print(f"  done  {label}: {rows:,} rows, {path.stat().st_size / 1e6:.1f} MB, {time.time() - start:.0f}s")
        done.append({
            "file": str(label),
            "source_url": url,
            "downloaded_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "bytes": path.stat().st_size,
            "rows": rows,
        })
    if done:
        _update_manifest(raw_dir, done)
    return failed


def show(raw_dir, names, years):
    """Print each planned file and whether it's on disk."""
    for name, year, path in planned_files(raw_dir, names, years):
        state = f"{path.stat().st_size / 1e6:7.1f} MB" if path.exists() else "  missing"
        print(f"  {state}  {path.relative_to(raw_dir)}")
