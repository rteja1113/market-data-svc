import datetime

import pytz

from iex_app.common.constants import MARKET_TZ


def convert_naive_datetime_in_utc_to_ist(
    utc_time: datetime.datetime,
) -> datetime.datetime:
    """
    Converts the given naive datetime object in UTC to Indian Standard Time
    """
    if utc_time.tzinfo is not None:
        raise ValueError("The given datetime object should not have a timezone")

    return utc_time.replace(tzinfo=pytz.utc).astimezone(MARKET_TZ)
