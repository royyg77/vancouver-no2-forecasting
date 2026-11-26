"""Download the raw inputs into data/raw/. Skips files that are already there.

Examples:
    python download_data.py                     # every source, every year
    python download_data.py --only no2 weather  # some sources
    python download_data.py --years 2023-2024   # some years
    python download_data.py --force             # download again
    python download_data.py --list              # what's on disk
"""

import argparse
import sys

from pipeline import config
from pipeline.download import SOURCES, download, show


def parse_years(text):
    """'2016' -> [2016]; '2015-2018' -> [2015, ..., 2018]."""
    first, _, last = text.partition("-")
    return list(range(int(first), int(last or first) + 1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only", nargs="+", choices=list(SOURCES), default=list(SOURCES), help="sources to fetch")
    p.add_argument("--years", type=parse_years, default=config.YEARS, help="e.g. 2024 or 2015-2024")
    p.add_argument("--force", action="store_true", help="download again even if the file exists")
    p.add_argument("--list", action="store_true", help="show which files are on disk, download nothing")
    args = p.parse_args()

    if args.list:
        show(config.RAW, args.only, args.years)
        return
    failed = download(config.RAW, args.only, args.years, force=args.force)
    if failed:
        print(f"\n{len(failed)} file(s) failed: {', '.join(failed)}. Run again to retry just those.")
        sys.exit(1)
    print("\nAll files present.")


if __name__ == "__main__":
    main()
