"""Raw files -> cleaned hourly grid. Needs the raw files in data/raw/.

Writes to data/clean/:
    clean_grid.parquet         one row per hour, 2015-2024, labelled by the start of the hour in UTC
    stations.parquet           air-quality stations (coordinates, coverage, proposal rule) and rain stations
    station_distances.parquet  km between every pair of air-quality stations
    flags.parquet              unusual NO2 hours, for review; nothing in the grid is changed by them

Prints every check on the way. The logic is in pipeline/clean.py.
"""

import numpy as np
import pandas as pd

from pipeline import clean, config

TARGETS = {"E316370": "Clark Drive", "E283549": "Tsawwassen"}
EXPECTED = {"no2_negatives": 116, "passing_rule": 27, "too_high": 3, "spikes_notebook_01": 3256}

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)


def show(title, value=""):
    print(f"\n== {title}")
    if isinstance(value, (pd.DataFrame, pd.Series)):
        print(value.to_string())
    elif value != "":
        print(value)


def main():
    hours = clean.grid_hours()
    station_list = config.RAW / "stations" / "bc_air_monitoring_stations.csv"

    # 1. BC pollutants
    long, raw_ids = {}, {}
    for pollutant in ["no2", "o3"]:
        data, checks = clean.load_bc(pollutant)
        show(f"{pollutant.upper()}: rows, stations and readings kept per year", checks["per_year"])
        print(f"unit: {checks['unit']} | negatives blanked: {checks['negatives_blanked']} | values that aren't numbers: {checks['unreadable']} | repeated (station, hour) pairs: {checks['duplicates']}")
        raw_ids[pollutant] = set(data["EMS_ID"])
        long[pollutant] = clean.merge_stations(data)
    print(f"\nNO2 negatives blanked: expected {EXPECTED['no2_negatives']}")

    # 2. stations
    stations = clean.merge_station_rows(clean.load_stations(station_list, raw_ids["no2"] | raw_ids["o3"]))
    no2_cov = clean.coverage_by_year(long["no2"])
    o3_cov = clean.coverage_by_year(long["o3"])
    share, passes = clean.coverage_rule(long["no2"])
    stations["has_o3"] = stations.index.isin(o3_cov.index)
    for year in config.YEARS:
        stations[f"no2_pct_{year}"] = no2_cov[year].reindex(stations.index)
    for year in config.YEARS:
        stations[f"o3_pct_{year}"] = o3_cov[year].reindex(stations.index)
    stations["rule_valid_days_pct"] = share.reindex(stations.index) * 100
    stations["passes_rule"] = passes.reindex(stations.index).astype(bool)

    show(f"stations: {len(stations)} air-quality stations ({len(raw_ids['no2'])} NO2 IDs, Agassiz merged), {int(stations['passes_rule'].sum())} pass the proposal rule (expected {EXPECTED['passing_rule']})")
    print("fail the rule:", ", ".join(f"{stations.loc[i, 'name']} ({stations.loc[i, 'rule_valid_days_pct']:.0f}% valid days)" for i in stations.index[~stations["passes_rule"]]))
    cov_table = no2_cov.round(0).astype(int)
    cov_table.index = [f"{stations.loc[i, 'name'][:34]} ({i})" for i in cov_table.index]
    show("NO2: % of hours with a value, station x year", cov_table.sort_index())

    distances = clean.distance_km(stations)
    for station, name in TARGETS.items():
        near = distances.loc[station].drop(station).nsmallest(3)
        print(f"nearest to {name}: " + ", ".join(f"{stations.loc[i, 'name']} {km:.2f} km" for i, km in near.items()))

    # 3. weather and rain
    yvr = clean.load_eccc("weather_yvr")
    weather = clean.yvr_weather(yvr)
    rain, rain_rows = {}, []
    for name, folder in clean.RAIN_FOLDERS.items():
        rain[name], info = clean.rain_station(clean.load_eccc(folder))
        rain_rows.append({**info, "kind": "rain", "grid_column": f"rain_{name}_mm"})

    # 4. hourly grid
    no2 = clean.to_wide(long["no2"], "no2_", hours)
    o3 = clean.to_wide(long["o3"], "o3_", hours)
    grid, dropped = clean.hourly_grid(hours, no2, o3, weather, rain)

    show(f"grid: {grid.shape[0]} rows x {grid.shape[1]} columns ({no2.shape[1]} NO2, {o3.shape[1]} O3, {weather.shape[1]} YVR weather, {len(rain)} rain)")
    steps = grid.index.to_series().diff().dropna().unique()
    print(f"one row per hour: {grid.index.is_unique and len(steps) == 1 and steps[0] == pd.Timedelta(hours=1) and len(grid) == len(hours)}")
    print(f"first/last row (UTC): {grid.index[0]} / {grid.index[-1]}")
    for pollutant, wide in [("no2", no2), ("o3", o3)]:
        same = (wide.notna().sum().rename(lambda c: c.split("_", 1)[1]) == long[pollutant].groupby("EMS_ID").size()).all()
        print(f"{pollutant.upper()} values per station in the grid match the load step: {same}")
    print("ECCC rows before 2015 or after 2024 (dropped):", dropped)

    local = grid.index.tz_convert(config.LOCAL_TZ)
    per_day = pd.Series(1, index=grid.index).groupby(local.date).size()
    odd_days = per_day[per_day != 24]
    show("clock-change days in local time (hours in the day)", odd_days.rename("hours").rename_axis("local date").to_frame().T)
    clark = grid[f"no2_{config.CLARK}"].to_numpy()
    weekday = local.day_of_week < 5
    local_day = local.tz_localize(None).normalize()
    peaks = {}
    for label, wanted in [("March", 23), ("November", 25)]:
        changes = [pd.Timestamp(d) for d, n in odd_days.items() if n == wanted]
        for side, lo, hi in [("4 weeks before", -28, -1), ("4 weeks after", 1, 28)]:
            in_window = np.zeros(len(grid), dtype=bool)
            for c in changes:
                in_window |= (local_day >= c + pd.Timedelta(days=lo)) & (local_day <= c + pd.Timedelta(days=hi))
            mask = weekday & in_window
            by_hour = pd.Series(clark[mask]).groupby(local.hour[mask]).mean()
            peaks[f"{label}, {side}"] = int(by_hour.loc[4:12].idxmax())
    print(f"{len(odd_days)} days: {sum(odd_days == 23)} with 23 hours (March), {sum(odd_days == 25)} with 25 hours (November)")
    print("Clark Drive weekday morning peak, local hour (4-12):", peaks)

    show("YVR weather: % of grid hours with a value, per variable", (weather.reindex(hours).notna().mean() * 100).round(2))
    calm = int((yvr["WIND_DIRECTION"] == 0).reindex(hours, fill_value=False).sum())
    print(f"hours with no YVR row at all: {int((~hours.isin(yvr.index)).sum())}")
    print(f"wind direction blank because calm (direction 0): {calm} hours = {calm / len(hours) * 100:.1f}%; wind direction with a value: {grid['yvr_wind_dir_deg'].notna().mean() * 100:.2f}%")
    print("ranges:", {c: (round(grid[c].min(), 2), round(grid[c].max(), 2)) for c in weather.columns})
    print(f"pressure mean: {grid['yvr_pressure_kpa'].mean():.2f} kPa")

    for name in rain:
        col = grid[f"rain_{name}_mm"]
        lst = grid.index.tz_convert(clean.BC_CLOCK)
        monthly = (col.notna().groupby([lst.year, lst.month]).mean() * 100).round(0).astype(int).unstack()
        monthly.index.name, monthly.columns.name = "year", "month"
        show(f"rain, {name}: % of hours with a value, by month (all: {col.notna().mean() * 100:.1f}%)", monthly)

    # 5. flags (on the grid's NO2, after negatives were blanked and Agassiz merged)
    flags, pairs = clean.flag_unusual(no2.rename(columns=lambda c: c.split("_", 1)[1]), stations)
    show("flags: cut-offs", {
        "spike": f"value - median of {clean.SPIKE_WINDOW} h around it > {clean.SPIKE_SCORE} x MAD (MAD floor {clean.SPIKE_MAD_FLOOR} ppb), not part of a run of such hours",
        "too_high": f"> {clean.TOO_HIGH_PPB} ppb",
        "off_neighbours": f"|robust z| > {clean.NEIGHBOUR_Z} for >= {clean.NEIGHBOUR_MIN_RUN} h in a row; z = (station - mean of 2 nearest - usual gap at that local hour) / (1.4826 x MAD at that hour, floor {clean.NEIGHBOUR_SCALE_FLOOR} ppb); only stations with correlation >= {clean.NEIGHBOUR_MIN_CORR} to that mean",
    })
    counts = flags.groupby("check").size()
    show("flags per check", counts)
    spikes_27 = int(((flags["check"] == "spike") & flags["station_id"].isin(stations.index[stations["passes_rule"]])).sum())
    print(f"spikes at the {int(stations['passes_rule'].sum())} stations that pass the rule: {spikes_27} (notebook 01: {EXPECTED['spikes_notebook_01']}); too_high expected {EXPECTED['too_high']}")
    per_station = flags.groupby(["station_id", "check"]).size().unstack(fill_value=0)
    per_station.index = [f"{stations.loc[i, 'name'][:34]} ({i})" for i in per_station.index]
    show("flags per station", per_station.sort_index())
    skipped = pairs[~pairs["checked"]]
    print("not checked against neighbours:", ", ".join(f"{stations.loc[i, 'name']} (corr {c:.2f})" for i, c in skipped["corr"].items()))

    named = flags.assign(name=stations.loc[flags["station_id"], "name"].to_numpy(), local=flags["start_utc"].dt.tz_convert(config.LOCAL_TZ).dt.strftime("%Y-%m-%d %H:%M"))
    show("top 10 spikes", named[named["check"] == "spike"].nlargest(10, "score")[["name", "local", "no2_ppb", "score"]].round(1))
    show("too_high", named[named["check"] == "too_high"][["name", "local", "no2_ppb"]].round(1))
    off = named[named["check"] == "off_neighbours"].copy()
    off["run_id"] = (off.groupby("station_id")["start_utc"].diff() != pd.Timedelta(hours=1)).cumsum()
    runs = off.groupby("run_id").agg(name=("name", "first"), start_local=("local", "first"), hours=("run_hours", "first"), max_abs_z=("score", lambda z: z.abs().max()), mean_no2=("no2_ppb", "mean"))
    show(f"off_neighbours: {len(runs)} runs; the 10 with the largest |z|", runs.nlargest(10, "max_abs_z").round(1).to_string(index=False))

    # station table: air-quality stations, then rain stations
    air_rows = stations.reset_index().assign(kind="air")
    table = pd.concat([air_rows, pd.DataFrame(rain_rows)], ignore_index=True)
    first = ["station_id", "kind", "name", "lat", "lon", "source_ids", "grid_column"]
    table = table[first + [c for c in table.columns if c not in first]]
    table["passes_rule"] = table["passes_rule"].astype("boolean")
    table["has_o3"] = table["has_o3"].astype("boolean")

    # save
    config.CLEAN.mkdir(parents=True, exist_ok=True)
    outputs = {
        "clean_grid.parquet": grid,
        "stations.parquet": table,
        "station_distances.parquet": distances,
        "flags.parquet": flags,
    }
    show("saved to data/clean/")
    for file, frame in outputs.items():
        path = config.CLEAN / file
        frame.to_parquet(path, compression="zstd")
        pd.testing.assert_frame_equal(pd.read_parquet(path), frame, check_freq=False)
        print(f"  {file}: {frame.shape[0]} rows x {frame.shape[1]} columns, {path.stat().st_size / 1e6:.1f} MB (read back: identical)")


if __name__ == "__main__":
    main()
