# btc-cent-forecast-01

BTC price forecaster for the make.fun `btc-cent-forecast-01` competition.
Python 3.13, stdlib only, offline, deterministic.

## Method

Mean reversion on the recent 4-hour log return. For each case, let `close`
be the last minute close at the checkpoint, `med_recent` the median of the
last 30 closes, and `med_old` the median of the closes 270 to 240 minutes
before the checkpoint. With `r = ln(med_recent / med_old)`, the forecast is
`close * exp(-0.075 * r)`, clamped to (0, 10,000,000) and rounded to a
5-decimal grid. A negative recent 4h return nudges the forecast above the
checkpoint close, and vice versa.

## Practice results

- 5-case MAE: **46,382.9 cents** vs persistence 47,054.7 cents (ratio 0.9857)
- 6-case MAE (secondary): **43,415.7 cents** vs persistence 44,076.2 cents

## Usage

```sh
MAKEFUN_INPUT_DIR=<input dir> MAKEFUN_OUTPUT_DIR=<output dir> python3 main.py
```
