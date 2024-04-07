import datetime

from src.common.constants import MARKET_TZ
from src.common.models import TimeFrame


def _convert_string_to_datetime(datetime_string: str) -> datetime.datetime:
    return MARKET_TZ.localize(
        datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    )


def convert_datetime_query_params_to_time_frame(
    start_datetime_str: str, end_datetime_str: str
) -> TimeFrame:
    start_datetime = _convert_string_to_datetime(start_datetime_str)
    end_datetime = _convert_string_to_datetime(end_datetime_str)
    return TimeFrame(start_datetime=start_datetime, end_datetime=end_datetime)
