from datetime import datetime

import pytest
from fastapi import HTTPException

from src.common.constants import MARKET_TZ
from src.common.models import TimeFrame
from src.marketdata.router_utils import (
    _convert_string_to_datetime,
    convert_datetime_query_params_to_time_frame,
)


def test__convert_string_to_datetime_with_valid_input():
    datetime_string = "2022-01-01 00:00:00"
    expected_datetime = MARKET_TZ.localize(datetime(2022, 1, 1, 0, 0, 0))
    assert _convert_string_to_datetime(datetime_string) == expected_datetime


def test__validate_and_convert_datetime_params_with_valid_input():
    start_datetime_str = "2022-01-01 00:00:00"
    end_datetime_str = "2022-01-02 00:00:00"
    expected_time_frame = TimeFrame(
        start_datetime=MARKET_TZ.localize(datetime(2022, 1, 1, 0, 0, 0)),
        end_datetime=MARKET_TZ.localize(datetime(2022, 1, 2, 0, 0, 0)),
    )
    assert (
        convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
        == expected_time_frame
    )


def test__validate_and_convert_datetime_params_with_invalid_dates():
    start_datetime_str = "2022-01-02 00:00:00"
    end_datetime_str = "2022-01-01 00:00:00"
    with pytest.raises(HTTPException):
        convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
