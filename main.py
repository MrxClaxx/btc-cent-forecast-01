#!/usr/bin/env python3
"""BTC cent forecaster for make.fun btc-cent-forecast-01.

Reads one case per "<id>.in" JSON file from MAKEFUN_INPUT_DIR and writes
"<id>.out" with a single price forecast to MAKEFUN_OUTPUT_DIR.

Method: mean reversion on the recent 4h log return. Let close be the last
minute close at the checkpoint, med_recent the median of the last 30 closes
and med_old the median of the closes 270 to 240 minutes before the
checkpoint. r = ln(med_recent / med_old); forecast = close * exp(-0.075 * r).
The forecast is clamped to (0, 10_000_000) and rounded to a 5-decimal grid.
A negative recent 4h return (med_recent below med_old) nudges the forecast
above the checkpoint close, and vice versa — a pure mean-reversion tilt.

Stdlib only, offline, deterministic: no randomness, no clock, no network.
"""

import json
import math
import os
import statistics
import sys
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999
MEAN_REVERSION = 0.075


def clamp_price(value: float) -> float:
    """Clamp to (0, 10_000_000) and round to a 5-decimal grid."""
    value = min(MAX_PRICE, max(MIN_PRICE, value))
    return round(value * 1e5) / 1e5


def forecast_price(prices: list) -> float:
    """Forecast the checkpoint close 240 minutes ahead."""
    close = prices[-1]
    if len(prices) < 270:
        # Not enough history for the old window: fall back to persistence.
        return clamp_price(close)
    med_recent = statistics.median(prices[-30:])
    med_old = statistics.median(prices[-270:-240])
    r = math.log(med_recent / med_old)
    return clamp_price(close * math.exp(-MEAN_REVERSION * r))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_files = sorted(INPUT_DIR.glob("*.in"))
    for input_path in input_files:
        case_id = input_path.stem
        with input_path.open("r", encoding="utf-8") as fh:
            case = json.load(fh)
        markets = case["markets"]
        if len(markets) != 1:
            raise ValueError(f"case {case_id}: expected exactly one market")
        prices = markets[0]["prices"]
        price = forecast_price(prices)
        payload = {"forecasts": [{"case": case_id, "price": price}]}
        output_path = OUTPUT_DIR / f"{case_id}.out"
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
