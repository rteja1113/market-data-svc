import datetime

import pytz

from src.common.constants import MARKET_TZ


def convert_timestamp_to_indian_datetime(
    unix_timestamp: int,
) -> datetime.datetime:
    """
    Converts the given naive datetime object in UTC to Indian Standard Time
    """
    utc_time = datetime.datetime.utcfromtimestamp(unix_timestamp)
    return utc_time.replace(tzinfo=pytz.utc).astimezone(MARKET_TZ)
