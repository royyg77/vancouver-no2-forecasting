"""Print a summary of one data file (.csv or .parquet). Read-only: never changes the file.

Examples:
    python inspect_data.py data/raw/weather_yvr/2024.csv
    python inspect_data.py --source weather --year 2024
    python inspect_data.py --source stations
    python inspect_data.py --source no2 --year 2023 --rows 10

A relative path is read from the repo folder, so it works from any directory.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from pipeline import config
from pipeline.download import SOURCES

TOP_VALUES_MAX_UNIQUE = 20 # show top values only for text columns with this many distinct values or fewer
TOP_VALUES = 5


def file_from_source(name, year):
    """Path of one raw file, built the same way as planned_files() in pipeline/download.py."""
    if name not in SOURCES:
        sys.exit(f"unknown source '{name}'. Valid sources: {', '.join(SOURCES)}")
    folder, pattern, per_year, _ = SOURCES[name]
    if per_year and year is None:
        sys.exit(f"source '{name}' has one file per year: add --year, e.g. --year {config.YEARS[-1]}")
    return config.RAW / folder / pattern.format(year=year)


def read(path):
    if path.suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8", low_memory=False) # low_memory=False: infer each column's type from the whole file
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    sys.exit(f"{path}: expected a .csv or .parquet file")


def heading(title):
    print(f"\n=== {title} ===")


def summarize(df, path, rows):
    heading("File")
    print(path)
    print(f"{len(df):,} rows x {df.shape[1]} columns")

    heading("Columns and dtypes")
    print(df.dtypes.to_string())

    heading(f"First {rows} rows")
    print(df.head(rows).to_string())

    heading("info()")
    df.info()

    heading("describe(), numeric columns")
    numeric = df.select_dtypes(include="number")
    print(numeric.describe().to_string() if numeric.shape[1] else "no numeric columns")

    heading("Missing values per column")
    missing = pd.DataFrame({"missing": df.isna().sum(), "%": (df.isna().mean() * 100).round(1)})
    print(missing.to_string())

    heading("Text columns: distinct values")
    text = df.select_dtypes(include=["object", "str"]) # pandas 3 loads text as "str"; "object" covers older files
    if not text.shape[1]:
        print("no text columns")
        return
    print(text.nunique().rename("distinct").to_string())
    for col in text:
        if text[col].nunique() <= TOP_VALUES_MAX_UNIQUE:
            print(f"\n{col}: top {TOP_VALUES}")
            print(text[col].value_counts(dropna=False).head(TOP_VALUES).to_string())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?", type=Path, help="a .csv or .parquet file")
    p.add_argument("--source", help=f"one of: {', '.join(SOURCES)}")
    p.add_argument("--year", type=int, help="needed for sources with one file per year")
    p.add_argument("--rows", type=int, default=5, help="rows to show from the top (default 5)")
    args = p.parse_args()

    if args.path and args.source:
        p.error("give a path or --source, not both")
    if args.source:
        path = file_from_source(args.source, args.year)
        fix = f"python download_data.py --only {args.source}" + (f" --years {args.year}" if args.year else "")
    elif args.path:
        path = args.path if args.path.is_absolute() else config.ROOT / args.path
        fix = "python download_data.py"
    else:
        p.error("give a path or --source")

    if not path.exists():
        sys.exit(f"{path} not found. To download the raw data, run: {fix}")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None) # fit the terminal
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_info_columns", 1000) # info() lists every column, not just a count

    summarize(read(path), path, args.rows)


if __name__ == "__main__":
    main()
