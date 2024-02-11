from __future__ import annotations

from datetime import timedelta

import pytz

# general constants
BASE_MARKET_URL = "https://www.iexindia.com/marketdata/"
STATE_ZONES = [
    "A1",
    "A2",
    "E1",
    "E2",
    "N1",
    "N2",
    "N3",
    "S1",
    "S2",
    "S3",
    "W1",
    "W2",
    "W3",
]
ALL_PRICE_COLUMNS = STATE_ZONES + ["MCP"]
PRICE_PER_UNIT_ENERGY_UNIT = "Rs/MWh"
MARKET_TIME_STEP_IN_MINUTES = 15
MARKET_TIME_DELTA = timedelta(minutes=MARKET_TIME_STEP_IN_MINUTES)
NUM_TIME_STEPS_IN_HOUR = 4
NUM_HOURS_IN_DAY = 24
NUM_TIME_STEPS_IN_DAY = NUM_TIME_STEPS_IN_HOUR * NUM_HOURS_IN_DAY
MARKET_TZ = pytz.timezone("Asia/Kolkata")
