"""Download hourly METAR/AWOS observations for the Bryan--College Station area.

Source: Iowa Environmental Mesonet (IEM) ASOS/AWOS archive, Iowa State
University Department of Agronomy.
    https://mesonet.agron.iastate.edu/request/download.phtml

Stations
--------
CFD : Coulter Field, Bryan, TX (30.7157 N, 96.3314 W, 102 m). Primary series.
CLL : Easterwood Field, College Station, TX (30.5881 N, 96.3639 W, 98 m).
      Long-record cross-check station, roughly 14.5 km south of Coulter Field.

Reproduce with:
    python data/fetch_asos.py

Writes data/raw/<station>_hourly.csv, one row per routine observation, with
times already converted to America/Chicago (so daylight saving time is handled
by the archive, not by this code).
"""

from __future__ import annotations

import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Final

IEM_ENDPOINT: Final[str] = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"

# Archive start dates reported by the IEM station metadata service
# (https://mesonet.agron.iastate.edu/api/1/network/TX_ASOS.geojson, accessed
# 2026-08-31): CFD begins 2013-05-02, CLL begins 1929-07-25. The CLL request is
# truncated to 1996 because that is well inside the period of continuous
# automated dew point reporting and is ample for a cross-check.
STATIONS: Final[dict[str, tuple[int, int, int]]] = {
    "CFD": (2013, 5, 2),
    "CLL": (1996, 1, 1),
}

END_DATE: Final[tuple[int, int, int]] = (2026, 8, 31)

RAW_DIR: Final[Path] = Path(__file__).resolve().parent / "raw"


def build_url(station: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> str:
    """Return the IEM download URL for one station's routine hourly observations."""
    params = {
        "station": station,
        "data": ["tmpf", "dwpf", "relh"],
        "year1": start[0],
        "month1": start[1],
        "day1": start[2],
        "year2": end[0],
        "month2": end[1],
        "day2": end[2],
        "tz": "America/Chicago",
        "format": "onlycomma",
        "latlon": "no",
        "elev": "no",
        "missing": "M",
        "trace": "T",
        "direct": "no",
        # report_type=3 restricts the download to routine hourly observations,
        # excluding SPECI reports triggered by rapidly changing conditions.
        "report_type": "3",
    }
    return f"{IEM_ENDPOINT}?{urllib.parse.urlencode(params, doseq=True)}"


def fetch(station: str, start: tuple[int, int, int], attempts: int = 4) -> str:
    """Download one station's archive, retrying on transient IEM failures."""
    url = build_url(station, start, END_DATE)
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=600) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001 - retry on any transport failure
            if attempt == attempts:
                raise
            print(f"  attempt {attempt} for {station} failed ({exc}); retrying")
            time.sleep(10 * attempt)
    raise RuntimeError("unreachable")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for station, start in STATIONS.items():
        print(f"fetching {station} from {start[0]}-{start[1]:02d}-{start[2]:02d} ...")
        text = fetch(station, start)
        out = RAW_DIR / f"{station.lower()}_hourly.csv"
        out.write_text(text, encoding="utf-8")
        n_rows = text.count("\n") - 1
        print(f"  wrote {out} ({n_rows:,} observations)")


if __name__ == "__main__":
    main()
