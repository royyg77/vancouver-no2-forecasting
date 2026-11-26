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
| `rain_burns_bog/{year}.csv` | hourly weather at Delta Burns Bog, used for rain | same API, climate ID 1102415 |

`manifest.csv` lists every file with its source, download date, size and row count. The BC archive can be revised, so the date says which version was used.

The files are saved as downloaded: no cleaning, no unit changes. NO2 times are local standard time (UTC-8), stamped at the end of the hour. Weather wind direction is in tens of degrees and speed in km/h.

## Cleaned grid

`build.py` needs only `data/clean/clean_grid.parquet`. `python clean_data.py` makes it from `data/raw/`, together with:

- `stations.parquet`: air-quality stations (coordinates, NO2 and O3 coverage per year, the proposal's coverage rule) and the three rain stations (coordinates)
- `station_distances.parquet`: km between every pair of air-quality stations
- `flags.parquet`: unusual NO2 hours, for review

Every column is listed in `data_dictionary.md`.

## Warning

`data/processed/hourly_grid.parquet`, written by notebook 01, is **UNCLEANED**. Don't train on it.

## Cleaning rules applied

Applied by `clean_data.py` (logic in `pipeline/clean.py`), first run 2026-11-26.

**Whole grid**
- One row per hour, 2015-01-01 00:00 to 2024-12-31 23:00 local standard time (87,672 rows), labelled by the **start** of the hour in UTC (`start_utc`).
- Nothing is filled: a missing reading stays blank. Nothing is deleted for looking odd: unusual NO2 hours are flagged in `flags.parquet` instead.

**NO2 and O3 (BC archive)**
- Rows with no value are dropped.
- End-of-hour shift: `DATE_PST` marks the end of the hour, so 1 hour is subtracted to get the start.
- Time zone: BC times are UTC−8 all year (no daylight saving); they are read as fixed UTC−8 and converted to UTC.
- Negative values are blanked: 116 for NO2, 824 for O3.
- The run stops if a pollutant has more than one unit (both are ppb only) or a repeated (station, hour) pair (there are none).
- Agassiz Municipal Hall (E293810, 2015–2023) and Agassiz Centennial Park (598, 2024 only), 0.90 km apart, are merged into one station under E293810. They never report the same hour.

**Stations**
- From the BC station list, the "… Met" rows (weather sensors at the same site) and "…_OLD" rows (old entries) are dropped, then the first row per EMS_ID is kept. All 32 NO2 IDs have coordinates; after the Agassiz merge there are 31 air-quality stations (27 also have O3).
- Proposal's coverage rule: a station passes if it has a valid daily mean (NO2 in at least 18 of the day's hours, local calendar days) on at least 75% of the days in 2016–2019. 27 stations pass. Stations that fail are kept in the grid.
- Distances between stations use the haversine formula (distance along the Earth's surface).

**YVR weather and rain (ECCC)**
- Rows are sorted by `UTC_DATE` (the API returns them out of order). The start of the hour is `UTC_DATE` − 1 hour, the same rule as for NO2.
- Rain (`PRECIP_AMOUNT`) is the amount in the hour ending at `UTC_DATE`. ECCC's documentation gives the unit (mm) but doesn't say which hour a timestamp covers. In the data, a wet hour at each rain station lines up best with YVR reporting rain one hour earlier or at the same time (correlation 0.71–0.76), and worse one hour later (0.61–0.63), which fits the hour ending at the timestamp.
- YVR units: wind direction × 10 (tens of degrees → degrees), wind speed ÷ 3.6 (km/h → m/s). Wind direction 0 means calm, not north: it is blanked (2,947 hours, 3.4%). Wind speed is kept.
- Kept from YVR: temperature, relative humidity, station pressure, wind speed, wind direction. YVR's own precipitation column is empty and is dropped.
- Rain is kept as measured at Vancouver Harbour, Delta Burns Bog and Vancouver Sea Island, gaps included. Filling Harbour's and Burns Bog's gaps from Sea Island happens in `build.py`, not here.
- The ECCC reading at 2015-01-01 00:00 local falls before the grid (it ends the hour 2014-12-31 23:00) and is dropped. The grid's last hour (2024-12-31 23:00 local) has no weather or rain: its reading is stamped 2025-01-01 00:00, in a 2025 file that isn't downloaded. So YVR is blank in 65 hours: 64 missing rows plus that last hour.

**Flags (NO2 only; nothing in the grid is changed)**
- `spike`: an hour more than 10 MADs (median absolute deviations, floor 0.5 ppb) above the median of the 25 hours around it, and not part of a run of such hours. Same rule as notebook 01, section 8. The rule looks at the hour after, so blanking any of these must be done by hand from a written list, never automatically.
- `too_high`: above 100 ppb.
- `off_neighbours`: the gap between a station and the mean of its two nearest stations is more than 6 robust standard deviations (1.4826 × MAD, floor 1 ppb) from that station's usual gap at the same local hour, for at least 6 hours in a row. Only for stations whose correlation with that mean is at least 0.5; seven stations aren't checked (Langdale and Horseshoe Bay track their neighbours poorly; Powell River, Squamish and Whistler have no two neighbours reporting at the same time).

