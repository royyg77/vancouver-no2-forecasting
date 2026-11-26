# Data dictionary

One line per column of each saved table. Tables are in `data/clean/`, made by `python clean_data.py`.

- `clean_grid`: `clean_grid.parquet`, one row per hour
- `stations`: `stations.parquet`, one row per air-quality or rain station
- `station_distances`: `station_distances.parquet`, km between air-quality stations
- `flags`: `flags.parquet`, unusual NO2 hours for review

| Column | Table | Meaning | Units | Time it comes from |
|---|---|---|---|---|
| `start_utc` (index) | clean_grid | start of the hour, one row per hour from 2015-01-01 00:00 to 2024-12-31 23:00 local standard time | UTC timestamp | — |
| `no2_0220204` | clean_grid | NO2 at Powell River Cranberry Lake; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0220205` | clean_grid | NO2 at Powell River Wildwood; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0310162` | clean_grid | NO2 at Port Moody Rocky Point Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0310172` | clean_grid | NO2 at Squamish Gov't Bldg; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0310174` | clean_grid | NO2 at Vancouver Robson Square; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0310177` | clean_grid | NO2 at Burnaby Kensington Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_0310179` | clean_grid | NO2 at North Vancouver Second Narrows; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E206270` | clean_grid | NO2 at Burnaby Mountain; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E206271` | clean_grid | NO2 at Surrey East; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E207417` | clean_grid | NO2 at Richmond South; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E207418` | clean_grid | NO2 at Burnaby South; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E207723` | clean_grid | NO2 at North Delta; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E209177` | clean_grid | NO2 at North Vancouver Mahon Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E209178` | clean_grid | NO2 at Langley Central; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E220891` | clean_grid | NO2 at Chilliwack Airport; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E222778` | clean_grid | NO2 at Langdale Elementary; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E223756` | clean_grid | NO2 at Hope Airport; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E227431` | clean_grid | NO2 at Whistler Meadow Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E232244` | clean_grid | NO2 at Pitt Meadows Meadowlands School; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E232245` | clean_grid | NO2 at Maple Ridge Golden Ears School; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E232246` | clean_grid | NO2 at Vancouver International Airport #2; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E238212` | clean_grid | NO2 at Abbotsford Central; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E242892` | clean_grid | NO2 at Coquitlam Douglas College; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E275843` | clean_grid | NO2 at Horseshoe Bay; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E283549` | clean_grid | NO2 at Tsawwassen; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E289309` | clean_grid | NO2 at Abbotsford A Columbia Street; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E293810` | clean_grid | NO2 at Agassiz Municipal Hall / Agassiz Centennial Park (2015–2023 Municipal Hall, 2024 Centennial Park); blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E302130` | clean_grid | NO2 at Mission School Works Yard; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E304570` | clean_grid | NO2 at Squamish Elementary; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E308566` | clean_grid | NO2 at New Westminster Sapperton Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `no2_E316370` | clean_grid | NO2 at Vancouver Clark Drive; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_0310162` | clean_grid | O3 at Port Moody Rocky Point Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_0310172` | clean_grid | O3 at Squamish Gov't Bldg; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_0310174` | clean_grid | O3 at Vancouver Robson Square; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_0310177` | clean_grid | O3 at Burnaby Kensington Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_0310179` | clean_grid | O3 at North Vancouver Second Narrows; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E206270` | clean_grid | O3 at Burnaby Mountain; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E206271` | clean_grid | O3 at Surrey East; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E207417` | clean_grid | O3 at Richmond South; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E207418` | clean_grid | O3 at Burnaby South; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E207723` | clean_grid | O3 at North Delta; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E209177` | clean_grid | O3 at North Vancouver Mahon Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E209178` | clean_grid | O3 at Langley Central; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E220891` | clean_grid | O3 at Chilliwack Airport; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E223756` | clean_grid | O3 at Hope Airport; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E227431` | clean_grid | O3 at Whistler Meadow Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E232244` | clean_grid | O3 at Pitt Meadows Meadowlands School; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E232245` | clean_grid | O3 at Maple Ridge Golden Ears School; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E232246` | clean_grid | O3 at Vancouver International Airport #2; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E238212` | clean_grid | O3 at Abbotsford Central; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E242892` | clean_grid | O3 at Coquitlam Douglas College; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E283549` | clean_grid | O3 at Tsawwassen; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E289309` | clean_grid | O3 at Abbotsford A Columbia Street; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E293810` | clean_grid | O3 at Agassiz Municipal Hall / Agassiz Centennial Park (2015–2023 Municipal Hall, 2024 Centennial Park); blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E302130` | clean_grid | O3 at Mission School Works Yard; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E304570` | clean_grid | O3 at Squamish Elementary; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E308566` | clean_grid | O3 at New Westminster Sapperton Park; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `o3_E316370` | clean_grid | O3 at Vancouver Clark Drive; blank = no reading or a negative value | ppb | the hour starting at `start_utc` (BC's end-of-hour stamp `DATE_PST` − 1 h, UTC−8 → UTC) |
| `yvr_temp_c` | clean_grid | air temperature at Vancouver airport (YVR) | °C | reading at the end of the hour (`UTC_DATE` = `start_utc` + 1 h) |
| `yvr_rh_pct` | clean_grid | relative humidity at YVR | % | reading at the end of the hour (`UTC_DATE` = `start_utc` + 1 h) |
| `yvr_pressure_kpa` | clean_grid | station pressure at YVR | kPa | reading at the end of the hour (`UTC_DATE` = `start_utc` + 1 h) |
| `yvr_wind_speed_ms` | clean_grid | wind speed at YVR (API km/h ÷ 3.6) | m/s | reading at the end of the hour (`UTC_DATE` = `start_utc` + 1 h) |
| `yvr_wind_dir_deg` | clean_grid | direction the wind blows from at YVR (API tens of degrees × 10); blank when calm (API direction 0) | degrees, 0/360 = north | reading at the end of the hour (`UTC_DATE` = `start_utc` + 1 h) |
| `rain_harbour_mm` | clean_grid | precipitation at VANCOUVER HARBOUR CS (climate ID 1108446), as measured, not filled | mm | total over the hour starting at `start_utc` (the hour ending at `UTC_DATE` = `start_utc` + 1 h; checked against YVR's hourly weather reports, see data/README.md) |
| `rain_burns_bog_mm` | clean_grid | precipitation at DELTA BURNS BOG (climate ID 1102415), as measured, not filled | mm | total over the hour starting at `start_utc` (the hour ending at `UTC_DATE` = `start_utc` + 1 h; checked against YVR's hourly weather reports, see data/README.md) |
| `rain_sea_island_mm` | clean_grid | precipitation at VANCOUVER SEA ISLAND CCG (climate ID 1108380), as measured, not filled | mm | total over the hour starting at `start_utc` (the hour ending at `UTC_DATE` = `start_utc` + 1 h; checked against YVR's hourly weather reports, see data/README.md) |
| `station_id` | stations | air-quality stations: BC EMS_ID (Agassiz merged under E293810); rain stations: ECCC climate ID | — | — |
| `kind` | stations | `air` (BC air-quality station) or `rain` (ECCC rain station) | — | — |
| `name` | stations | station name (air: BC station list `STATION_NAME_FULL`; rain: ECCC `STATION_NAME`) | — | — |
| `lat`, `lon` | stations | station coordinates (air: BC station list; rain: from the ECCC files) | decimal degrees | — |
| `source_ids` | stations | air stations: the raw EMS_ID(s) merged into this row (`E293810 + 598` for Agassiz) | — | — |
| `grid_column` | stations | rain stations: the grid column holding its rain (air stations use `no2_<station_id>` and `o3_<station_id>`) | — | — |
| `has_o3` | stations | air stations: the station has an O3 column in the grid | yes/no | — |
| `no2_pct_2015` … `no2_pct_2024` | stations | air stations: % of hours in that year with a NO2 value (after negatives blanked) | % | local standard year (UTC−8) |
| `o3_pct_2015` … `o3_pct_2024` | stations | air stations: same for O3; blank if the station has no O3 | % | local standard year (UTC−8) |
| `rule_valid_days_pct` | stations | air stations: % of days in 2016–2019 with a valid daily mean (NO2 in ≥ 18 of the day's hours) | % | local calendar days (America/Vancouver) |
| `passes_rule` | stations | air stations: the proposal's coverage rule, `rule_valid_days_pct` ≥ 75 | yes/no | 2016–2019 |
| one column per `station_id` | station_distances | distance between the row's and the column's air-quality station along the Earth's surface (haversine) | km | — |
| `station_id` | flags | air-quality station flagged | — | — |
| `start_utc` | flags | start of the flagged hour (same label as the grid) | UTC timestamp | — |
| `check` | flags | `spike`, `too_high` or `off_neighbours` (see data/README.md, cleaning rules) | — | — |
| `no2_ppb` | flags | the flagged NO2 value, unchanged in the grid | ppb | the flagged hour |
| `score` | flags | `spike`: MADs above the 25-hour median; `off_neighbours`: robust z-score of the gap to the two nearest stations; blank for `too_high` | — | the flagged hour |
| `run_hours` | flags | `off_neighbours`: length of the run of hours the flag belongs to; blank otherwise | hours | — |
