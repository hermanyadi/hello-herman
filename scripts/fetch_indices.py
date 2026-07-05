"""
Fetches all Nifty indices from NSE India's public allIndices endpoint and
writes a cleaned-up snapshot to data/latest.json for the static dashboard.

Cleanup applied (NSE's raw JSON is inconsistent):
  - pe / pb / dy / advances / declines / unchanged arrive as strings -> converted to numbers
  - "0" or missing yearHigh/yearLow (common for niche indices) -> kept as null instead of 0
  - null reference dates -> left as null, dashboard handles it
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

NSE_API = "https://www.nseindia.com/api/allIndices"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")


def to_number(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_index(raw):
    year_high = to_number(raw.get("yearHigh"))
    year_low = to_number(raw.get("yearLow"))
    return {
        "key": raw.get("key"),
        "index": raw.get("index"),
        "indexSymbol": raw.get("indexSymbol"),
        "last": to_number(raw.get("last")),
        "variation": to_number(raw.get("variation")),
        "percentChange": to_number(raw.get("percentChange")),
        "open": to_number(raw.get("open")),
        "high": to_number(raw.get("high")),
        "low": to_number(raw.get("low")),
        "previousClose": to_number(raw.get("previousClose")),
        "yearHigh": year_high if year_high else None,
        "yearLow": year_low if year_low else None,
        "pe": to_number(raw.get("pe")),
        "pb": to_number(raw.get("pb")),
        "dy": to_number(raw.get("dy")),
        "advances": to_number(raw.get("advances")),
        "declines": to_number(raw.get("declines")),
        "unchanged": to_number(raw.get("unchanged")),
        "perChange30d": to_number(raw.get("perChange30d")),
        "perChange365d": to_number(raw.get("perChange365d")),
    }


def fetch_with_retries(max_attempts=4):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(NSE_API, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
            indices = payload.get("data", [])
            if not indices:
                raise ValueError("Empty 'data' field in NSE response")
            return indices, payload.get("timestamp")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"Attempt {attempt}/{max_attempts} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise RuntimeError(f"All {max_attempts} attempts failed: {last_error}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    raw_indices, nse_timestamp = fetch_with_retries()
    cleaned = [clean_index(idx) for idx in raw_indices]

    output = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "nse_timestamp": nse_timestamp,
        "count": len(cleaned),
        "indices": cleaned,
    }
    with open(LATEST_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(cleaned)} indices -> {LATEST_PATH}")


if __name__ == "__main__":
    main()
