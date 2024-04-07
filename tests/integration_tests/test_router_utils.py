from datetime import datetime

import pytest

from src.common.constants import MARKET_TZ
from src.common.models import TimeFrame
from src.marketdata.router_utils import convert_datetime_query_params_to_time_frame


@pytest.fixture
def start_datetime_string():
    return "2022-01-01 00:00:00"


@pytest.fixture
def end_datetime_string():
    return "2022-01-01 23:00:00"


def test_convert_datetime_query_params_to_time_frame_valid_input(
    start_datetime_string, end_datetime_string
):
    actual_time_frame = convert_datetime_query_params_to_time_frame(
        start_datetime_string, end_datetime_string
    )
    expected_time_frame = TimeFrame(
        start_datetime=MARKET_TZ.localize(datetime(2022, 1, 1, 0, 0, 0)),
        end_datetime=MARKET_TZ.localize(datetime(2022, 1, 1, 23, 0, 0)),
    )
    assert actual_time_frame == expected_time_frame


def test_convert_datetime_query_params_to_time_frame_invalid_input(
    start_datetime_string, end_datetime_string
):
    with pytest.raises(ValueError):
        convert_datetime_query_params_to_time_frame(
            end_datetime_string, start_datetime_string
        )
