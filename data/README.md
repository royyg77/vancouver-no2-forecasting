# Data

Only this file is in git. A fresh clone won't have `raw/`, `processed/` or `clean/`.

## Cleaned grid

`build.py` needs only `data/clean/clean_grid.parquet`. It doesn't exist yet.

## Raw inputs (needed only for cleaning)

- `data/raw/`: ten `{year}_NO2.csv` files for 2015-2024, and `2024_bc_air_monitoring_stations.csv`
- `data/processed/`: `weather_yvr.parquet`

## Warning

`data/processed/hourly_grid.parquet`, written by notebook 01, is **UNCLEANED**. Don't train on it.

## Cleaning rules applied

