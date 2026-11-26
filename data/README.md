# Data

Only this file is in git. A fresh clone has no data: run `python download_data.py` from the repo root.

## Raw inputs (`data/raw/`, made by `download_data.py`)

| Folder | What | Source |
|---|---|---|
| `no2/{year}.csv` | hourly NO2, Lower Mainland only, 2015-2024 | BC verified hourly air quality archive, `ftp://ftp.env.gov.bc.ca/pub/outgoing/AIR/AnnualSummary/{year}/NO2.csv` |
| `o3/{year}.csv` | hourly O3, Lower Mainland only, 2015-2024 | same archive, `{year}/O3.csv` |
| `stations/bc_air_monitoring_stations.csv` | station names and coordinates | same archive, 2024 folder |
| `weather_yvr/{year}.csv` | hourly weather at Vancouver airport, unchanged from the API | ECCC climate-hourly API, climate ID 1108395 |
| `rain_sea_island/{year}.csv` | hourly weather at Vancouver Sea Island, used for rain (YVR has no hourly precipitation) | same API, climate ID 1108380 |
| `rain_harbour/{year}.csv` | hourly weather at Vancouver Harbour, used for rain | same API, climate ID 1108446 |

`manifest.csv` lists every file with its source, download date, size and row count. The BC archive can be revised, so the date says which version was used.

The files are saved as downloaded: no cleaning, no unit changes. NO2 times are local standard time (UTC-8), stamped at the end of the hour. Weather wind direction is in tens of degrees and speed in km/h.

## Cleaned grid

`build.py` needs only `data/clean/clean_grid.parquet`. It doesn't exist yet.

## Warning

`data/processed/hourly_grid.parquet`, written by notebook 01, is **UNCLEANED**. Don't train on it.

## Cleaning rules applied

