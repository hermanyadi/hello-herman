"""
Fetches all ETFs from NSE India's public etf endpoint and writes a cleaned-up
snapshot to data/etf.json for the static dashboard.

Cleanup applied (NSE's raw JSON is inconsistent, same spirit as fetch_indices.py):
  - Almost every numeric field arrives as a string -> converted to numbers
  - yPC / mPC can arrive as the literal string "Infinity" for new ETFs with
    no 1-year history yet -> stored as null instead
  - Duplicate/legacy keys (XDt, CAct, YPC, MPC, stockIndClosePrice, series,
    chart*Path) are dropped -- not used by the dashboard
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

NSE_API = "https://www.nseindia.com/api/etf"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ETF_PATH = os.path.join(DATA_DIR, "etf.json")


def to_number(value):
    if value is None or value == "" or value == "-":
        return None
    if isinstance(value, str) and value.strip().lower() in ("infinity", "-infinity", "nan"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_etf(raw):
    return {
        "symbol": raw.get("symbol"),
        "assets": raw.get("assets"),
        "last": to_number(raw.get("ltP")),
        "percentChange": to_number(raw.get("per")),
        "change": to_number(raw.get("chn")),
        "open": to_number(raw.get("open")),
        "high": to_number(raw.get("high")),
        "low": to_number(raw.get("low")),
        "volume": to_number(raw.get("qty")),
        "tradedValue": to_number(raw.get("trdVal")),
        "nav": to_number(raw.get("nav")),
        "yearHigh": to_number(raw.get("wkhi")),
        "yearLow": to_number(raw.get("wklo")),
        "nearYearHigh": to_number(raw.get("nearWKH")),
        "nearYearLow": to_number(raw.get("nearWKL")),
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
            etfs = payload.get("data", [])
            if not etfs:
                raise ValueError("Empty 'data' field in NSE response")
            return etfs, payload.get("timestamp")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"Attempt {attempt}/{max_attempts} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise RuntimeError(f"All {max_attempts} attempts failed: {last_error}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    raw_etfs, nse_timestamp = fetch_with_retries()
    cleaned = [clean_etf(e) for e in raw_etfs]

    output = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "nse_timestamp": nse_timestamp,
        "count": len(cleaned),
        "etfs": cleaned,
    }
    with open(ETF_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(cleaned)} ETFs -> {ETF_PATH}")


if __name__ == "__main__":
    main()
