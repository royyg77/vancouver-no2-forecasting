"""Raw NO2, O3, station list, weather and rain -> cleaned hourly grid.

One function per cleaning step; clean_data.py runs them in order, prints the
checks and saves the results. Rules for the whole grid:
- each row is labelled with the start of its hour, in UTC
- nothing is filled: a missing reading stays blank
- nothing is deleted for looking odd: it is flagged instead (see flag_unusual)
"""

import numpy as np
import pandas as pd

from pipeline import config

BC_CLOCK = "Etc/GMT+8" # fixed UTC-8, no daylight saving (the sign in this name is reversed on purpose)
FIRST_HOUR = "2015-01-01 00:00" # local standard time
LAST_HOUR = "2024-12-31 23:00" # local standard time

# Agassiz Municipal Hall (E293810, 2015-2023) and Agassiz Centennial Park (598, 2024 only),
# 0.90 km apart, become one station under the older ID
MERGES = {"598": "E293810"} # ID that goes -> ID that stays

RAIN_FOLDERS = {"harbour": "rain_harbour", "burns_bog": "rain_burns_bog", "sea_island": "rain_sea_island"}

# proposal's coverage rule -> 75% of data required to count 
RULE_MIN_HOURS = 18 # hours with a value for a valid day
RULE_MIN_SHARE = 0.75 # share of valid days needed
RULE_YEARS = (2016, 2019)

# flag checks (notebook 01, section 8, for the spike rule)
TOO_HIGH_PPB = 100
SPIKE_WINDOW = 25 # hours, centred on the hour being checked
SPIKE_MIN_HOURS = 13 # values needed in the window
SPIKE_MAD_FLOOR = 0.5 # ppb, so a flat stretch doesn't turn tiny wiggles into huge scores
SPIKE_SCORE = 10 # MADs above the window median
NEIGHBOUR_MIN_CORR = 0.5 # check only stations that usually track their two nearest stations
NEIGHBOUR_Z = 6 # robust z-score of (station - mean of its two nearest stations)
NEIGHBOUR_MIN_RUN = 6 # hours in a row
NEIGHBOUR_SCALE_FLOOR = 1.0 # ppb


def grid_hours():
    """Every hour of 2015-2024 in local standard time, as UTC start-of-hour labels."""
    hours = pd.date_range(FIRST_HOUR, LAST_HOUR, freq="h", tz=BC_CLOCK).tz_convert("UTC").as_unit("us")
    hours.name = "start_utc"
    return hours


# ---------- load BC pollutants ----------

def to_start_of_hour(date_pst):
    """BC stamps each hour at its end ("01:00" is 00:00-01:00): subtract one hour. Still UTC-8, no time zone attached."""
    return pd.to_datetime(date_pst, format="%Y-%m-%d %H:%M") - pd.Timedelta(hours=1)


def to_utc(start_pst):
    """Read UTC-8 times (no daylight saving) and convert them to UTC."""
    return start_pst.dt.tz_localize(BC_CLOCK).dt.tz_convert("UTC").dt.as_unit("us")


def load_bc(pollutant, years=config.YEARS):
    """One pollutant's yearly BC files -> (long table: EMS_ID, start_utc, value; checks).

    Rows with no value are dropped and negative values are blanked (dropped too,
    since the table is long). Stops if a file has two units or a repeated (station, hour).
    """
    parts = []
    for year in years:
        part = pd.read_csv(config.RAW / pollutant / f"{year}.csv", usecols=["DATE_PST", "EMS_ID", "RAW_VALUE", "UNIT"], dtype=str, encoding="utf-8")
        parts.append(part.assign(file_year=year))
    raw = pd.concat(parts, ignore_index=True)
    raw["EMS_ID"] = raw["EMS_ID"].str.strip()
    value = pd.to_numeric(raw["RAW_VALUE"], errors="coerce")
    start_utc = to_utc(to_start_of_hour(raw["DATE_PST"]))

    units = sorted(raw["UNIT"].dropna().unique())
    if len(units) != 1:
        raise ValueError(f"{pollutant}: expected one unit, found {units}")
    duplicates = int(pd.DataFrame({"id": raw["EMS_ID"], "t": start_utc}).duplicated().sum())
    if duplicates:
        raise ValueError(f"{pollutant}: {duplicates} repeated (station, hour) pairs")

    negative = value < 0
    long = pd.DataFrame({"EMS_ID": raw["EMS_ID"], "start_utc": start_utc, "value": value.mask(negative)})
    long = long.dropna(subset=["value"]).reset_index(drop=True)
    checks = {
        "per_year": pd.DataFrame({
            "rows": raw.groupby("file_year").size(),
            "stations": raw.groupby("file_year")["EMS_ID"].nunique(),
            "readings_kept": long.groupby(long["start_utc"].dt.tz_convert(BC_CLOCK).dt.year).size(),
        }),
        "unit": units[0],
        "unreadable": int((value.isna() & raw["RAW_VALUE"].fillna("").str.strip().ne("")).sum()),
        "negatives_blanked": int(negative.sum()),
        "duplicates": duplicates,
    }
    return long, checks


def merge_stations(long, merges=MERGES):
    """Give merged sites one ID. Stops if two merged sites ever report the same hour."""
    ids = long["EMS_ID"].replace(merges)
    overlap = int(pd.DataFrame({"id": ids, "t": long["start_utc"]}).duplicated().sum())
    if overlap:
        raise ValueError(f"merged sites overlap in {overlap} hours")
    return long.assign(EMS_ID=ids)


# ---------- stations ----------

def load_stations(path, ems_ids):
    """Station list -> one row per station (name, lat, lon) for the given IDs.

    Drops the "... Met" rows (weather sensors at the same site) and "..._OLD" rows
    (old entries), then keeps the first row per EMS_ID.
    """
    st = pd.read_csv(path, dtype=str, encoding="utf-8")
    st["EMS_ID"] = st["EMS_ID"].str.strip()
    full = st["STATION_NAME_FULL"].str.strip()
    st = st[~full.str.endswith(" Met") & ~full.str.endswith("_OLD")].drop_duplicates("EMS_ID")
    st = st[st["EMS_ID"].isin(ems_ids)]
    missing = sorted(set(ems_ids) - set(st["EMS_ID"]))
    if missing:
        raise ValueError(f"not in the station list: {missing}")
    out = pd.DataFrame({
        "name": st["STATION_NAME_FULL"].str.strip().str.replace(r"_\d+$", "", regex=True).to_numpy(), # Powell River "_1" suffix
        "lat": st["LAT"].astype(float).to_numpy(),
        "lon": st["LONG"].astype(float).to_numpy(),
    }, index=pd.Index(st["EMS_ID"].to_numpy(), name="station_id"))
    if out[["lat", "lon"]].isna().any(axis=None):
        raise ValueError("stations without coordinates: " + ", ".join(out.index[out[["lat", "lon"]].isna().any(axis=1)]))
    return out.sort_index()


def merge_station_rows(stations, merges=MERGES):
    """One row per merged station: the kept ID's coordinates, both names, and both source IDs."""
    out = stations.assign(source_ids=stations.index.to_numpy())
    for gone, kept in merges.items():
        out.loc[kept, "name"] = f"{out.loc[kept, 'name']} / {out.loc[gone, 'name']}"
        out.loc[kept, "source_ids"] = f"{kept} + {gone}"
        out = out.drop(gone)
    return out


def coverage_by_year(long, years=config.YEARS):
    """% of hours with a value, station x year (years in local standard time)."""
    year = long["start_utc"].dt.tz_convert(BC_CLOCK).dt.year
    counts = long.groupby([long["EMS_ID"], year]).size().unstack(fill_value=0).reindex(columns=years, fill_value=0)
    hours = pd.Series({y: 8784 if y % 4 == 0 else 8760 for y in years})
    return counts.div(hours, axis=1).mul(100)


def coverage_rule(long):
    """Proposal's rule -> (share of valid days in the rule years, passes yes/no), per station.

    A valid day has a value in at least 18 of its hours. Days are local calendar
    days, as in notebook 01, which set the expected count of 27.
    """
    day = long["start_utc"].dt.tz_convert(config.LOCAL_TZ).dt.date.rename("day")
    hours_per_day = long.groupby([long["EMS_ID"], day]).size().reset_index(name="hours")
    first, last = RULE_YEARS
    in_years = pd.to_datetime(hours_per_day["day"]).dt.year.between(first, last)
    valid = hours_per_day[in_years & (hours_per_day["hours"] >= RULE_MIN_HOURS)]
    n_days = len(pd.date_range(f"{first}-01-01", f"{last}-12-31", freq="D"))
    share = (valid.groupby("EMS_ID").size() / n_days).reindex(long["EMS_ID"].unique(), fill_value=0.0)
    return share, share >= RULE_MIN_SHARE


def distance_km(stations):
    """Distance between every pair of stations along the Earth's surface (haversine), in km."""
    lat = np.radians(stations["lat"].to_numpy())[:, None]
    lon = np.radians(stations["lon"].to_numpy())[:, None]
    h = np.sin((lat.T - lat) / 2) ** 2 + np.cos(lat) * np.cos(lat.T) * np.sin((lon.T - lon) / 2) ** 2
    km = 2 * 6371 * np.arcsin(np.sqrt(h))
    return pd.DataFrame(km, index=stations.index, columns=stations.index)


# ---------- weather and rain ----------

def load_eccc(folder, years=config.YEARS):
    """One ECCC station's yearly files -> raw columns, indexed by start_utc, in time order.

    UTC_DATE is the end of the hour (rain is the amount in the hour ending then),
    so the start of the hour is UTC_DATE - 1 hour, the same rule as for NO2.
    """
    raw = pd.concat((pd.read_csv(config.RAW / folder / f"{y}.csv", low_memory=False) for y in years), ignore_index=True)
    raw = raw.sort_values("UTC_DATE") # the API returns rows out of time order
    raw["start_utc"] = (pd.to_datetime(raw["UTC_DATE"], format="%Y-%m-%dT%H:%M:%S").dt.tz_localize("UTC") - pd.Timedelta(hours=1)).dt.as_unit("us")
    if raw["start_utc"].duplicated().any():
        raise ValueError(f"{folder}: repeated hours")
    return raw.set_index("start_utc")


def yvr_weather(raw):
    """YVR raw columns -> the kept weather variables, in SI units. Calm hours get a blank direction."""
    calm = raw["WIND_DIRECTION"] == 0 # 0 means no direction, not north
    return pd.DataFrame({
        "yvr_temp_c": raw["TEMP"],
        "yvr_rh_pct": raw["RELATIVE_HUMIDITY"],
        "yvr_pressure_kpa": raw["STATION_PRESSURE"],
        "yvr_wind_speed_ms": raw["WIND_SPEED"] / 3.6, # km/h -> m/s
        "yvr_wind_dir_deg": (raw["WIND_DIRECTION"] * 10).mask(calm), # tens of degrees -> degrees
    }, index=raw.index)


def rain_station(raw):
    """One rain station's raw columns -> (rain in mm as measured, station row: id, name, lat, lon)."""
    info = {}
    for key, col in [("station_id", "CLIMATE_IDENTIFIER"), ("name", "STATION_NAME"), ("lat", "LATITUDE_DECIMAL_DEGREES"), ("lon", "LONGITUDE_DECIMAL_DEGREES")]:
        values = raw[col].dropna().unique()
        if len(values) != 1:
            raise ValueError(f"{col}: expected one value, found {list(values)[:5]}")
        info[key] = values[0]
    info["station_id"] = str(info["station_id"])
    return raw["PRECIP_AMOUNT"], info


# ---------- flag unusual NO2 ----------

def _runs(mask):
    """Length of the run of consecutive True values that each True value belongs to (0 where False)."""
    run_id = (mask != mask.shift()).cumsum()
    length = mask.groupby(run_id).transform("size")
    return length.where(mask, 0)


def flag_unusual(no2, stations):
    """Wide NO2 (hours x station) and station coordinates -> (flag table, neighbour pairs used).

    Flags only; no value is changed. One row per flagged (station, hour, check):
    - spike: one hour far above the median of the 25 hours around it (notebook 01, section 8)
    - too_high: above 100 ppb
    - off_neighbours: far from the mean of the station's two nearest stations for
      several hours in a row, at a station that usually tracks them. The gap is
      compared with that station's usual gap at the same hour of the day.
    """
    km = distance_km(stations)
    local_hour = no2.index.tz_convert(config.LOCAL_TZ).hour
    rows, pairs = [], []
    for station in no2.columns:
        s = no2[station]

        med = s.rolling(SPIKE_WINDOW, center=True, min_periods=SPIKE_MIN_HOURS).median()
        mad = (s - med).abs().rolling(SPIKE_WINDOW, center=True, min_periods=SPIKE_MIN_HOURS).median()
        score = (s - med) / mad.clip(lower=SPIKE_MAD_FLOOR)
        lone = (score > SPIKE_SCORE) & ~(score.shift(1) > SPIKE_SCORE) & ~(score.shift(-1) > SPIKE_SCORE)
        found = [pd.DataFrame({"start_utc": s.index[lone], "check": "spike", "no2_ppb": s[lone].to_numpy(), "score": score[lone].to_numpy(), "run_hours": np.nan})]

        high = s > TOO_HIGH_PPB
        found.append(pd.DataFrame({"start_utc": s.index[high], "check": "too_high", "no2_ppb": s[high].to_numpy(), "score": np.nan, "run_hours": np.nan}))

        near = km.loc[station].drop(station).nsmallest(2)
        reference = no2[near.index].mean(axis=1, skipna=False) # both neighbours needed
        corr = s.corr(reference)
        checked = bool(corr >= NEIGHBOUR_MIN_CORR)
        pairs.append({"station_id": station, "neighbour_1": near.index[0], "km_1": near.iloc[0], "neighbour_2": near.index[1], "km_2": near.iloc[1], "corr": corr, "checked": checked})
        if checked:
            gap = s - reference
            usual = gap.groupby(local_hour).transform("median")
            spread = 1.4826 * (gap - usual).abs().groupby(local_hour).transform("median") # robust standard deviation
            z = (gap - usual) / spread.clip(lower=NEIGHBOUR_SCALE_FLOOR)
            run = _runs(z.abs() > NEIGHBOUR_Z)
            off = run >= NEIGHBOUR_MIN_RUN
            found.append(pd.DataFrame({"start_utc": s.index[off], "check": "off_neighbours", "no2_ppb": s[off].to_numpy(), "score": z[off].to_numpy(), "run_hours": run[off].to_numpy(dtype=float)}))

        rows += [f.assign(station_id=station) for f in found]
    flags = pd.concat(rows, ignore_index=True)[["station_id", "start_utc", "check", "no2_ppb", "score", "run_hours"]].sort_values(["station_id", "start_utc", "check"]).reset_index(drop=True)
    return flags, pd.DataFrame(pairs).set_index("station_id")


# ---------- hourly grid ----------

def to_wide(long, prefix, hours):
    """Long (EMS_ID, start_utc, value) -> one column per station on the full hourly index. Stops if a reading falls outside it."""
    wide = long.pivot(index="start_utc", columns="EMS_ID", values="value")
    outside = int((~wide.index.isin(hours)).sum())
    if outside:
        raise ValueError(f"{prefix}: {outside} hours outside 2015-2024")
    wide = wide.reindex(hours)
    wide.columns = [f"{prefix}{c}" for c in wide.columns]
    return wide


def hourly_grid(hours, no2, o3, weather, rain):
    """Wide NO2, wide O3, YVR weather and rain series -> the grid. Nothing filled.

    Returns (grid, rows dropped per weather/rain source because they fall outside 2015-2024).
    """
    dropped = {"yvr": int((~weather.index.isin(hours)).sum())}
    parts = [no2, o3, weather.reindex(hours)]
    for name, series in rain.items():
        dropped[f"rain_{name}"] = int((~series.index.isin(hours)).sum())
        parts.append(series.reindex(hours).rename(f"rain_{name}_mm"))
    grid = pd.concat(parts, axis=1)
    grid.index.name = "start_utc"
    return grid, dropped
