from datetime import datetime

import pytest
from fastapi import HTTPException

from src.common.constants import MARKET_TZ
from src.common.enums import Markets
from src.common.models import TimeFrame
from src.marketdata.models import (
    BasePointInTimePriceDataDb,
    DAMPointInTimePriceDataDb,
    RTMPointInTimePriceDataDb,
)
from src.marketdata.router_utils import (
    _convert_orm_model_to_pydantic_model,
    _convert_string_to_datetime,
    _validate_and_convert_datetime_params,
)
from src.marketdata.schemas import DAMPointInTimePriceData, RTMPointInTimePriceData


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
        _validate_and_convert_datetime_params(start_datetime_str, end_datetime_str)
        == expected_time_frame
    )


def test__validate_and_convert_datetime_params_with_invalid_dates():
    start_datetime_str = "2022-01-02 00:00:00"
    end_datetime_str = "2022-01-01 00:00:00"
    with pytest.raises(HTTPException):
        _validate_and_convert_datetime_params(start_datetime_str, end_datetime_str)


def test__convert_orm_model_to_pydantic_model_with_dam_instance():
    settlement_period_start_datetime = datetime(2022, 1, 1, 0, 0, 0)
    orm_instance = DAMPointInTimePriceDataDb(
        settlement_period_start_timestamp=settlement_period_start_datetime.timestamp(),
        a1_price_in_rs_per_mwh=100,
        a2_price_in_rs_per_mwh=200,
        e1_price_in_rs_per_mwh=300,
        e2_price_in_rs_per_mwh=400,
        n1_price_in_rs_per_mwh=500,
        n2_price_in_rs_per_mwh=600,
        n3_price_in_rs_per_mwh=700,
        s1_price_in_rs_per_mwh=800,
        s2_price_in_rs_per_mwh=900,
        s3_price_in_rs_per_mwh=1000,
        w1_price_in_rs_per_mwh=1100,
        w2_price_in_rs_per_mwh=1200,
        w3_price_in_rs_per_mwh=1300,
        mcp_price_in_rs_per_mwh=1400,
    )
    result = _convert_orm_model_to_pydantic_model(
        settlement_period_start_datetime, orm_instance, Markets.DAM
    )
    assert isinstance(result, DAMPointInTimePriceData)


def test__convert_orm_model_to_pydantic_model_with_rtm_instance():
    settlement_period_start_datetime = datetime(2022, 1, 1, 0, 0, 0)
    orm_instance = RTMPointInTimePriceDataDb(
        settlement_period_start_timestamp=settlement_period_start_datetime.timestamp(),
        a1_price_in_rs_per_mwh=100,
        a2_price_in_rs_per_mwh=200,
        e1_price_in_rs_per_mwh=300,
        e2_price_in_rs_per_mwh=400,
        n1_price_in_rs_per_mwh=500,
        n2_price_in_rs_per_mwh=600,
        n3_price_in_rs_per_mwh=700,
        s1_price_in_rs_per_mwh=800,
        s2_price_in_rs_per_mwh=900,
        s3_price_in_rs_per_mwh=1000,
        w1_price_in_rs_per_mwh=1100,
        w2_price_in_rs_per_mwh=1200,
        w3_price_in_rs_per_mwh=1300,
        mcp_price_in_rs_per_mwh=1400,
    )
    result = _convert_orm_model_to_pydantic_model(
        settlement_period_start_datetime, orm_instance, Markets.RTM
    )
    assert isinstance(result, RTMPointInTimePriceData)


def test__convert_orm_model_to_pydantic_model_with_invalid_market():
    settlement_period_start_datetime = datetime(2022, 1, 1, 0, 0, 0)
    orm_instance = BasePointInTimePriceDataDb(
        a1_price_in_rs_per_mwh=100,
        a2_price_in_rs_per_mwh=200,
        e1_price_in_rs_per_mwh=300,
        e2_price_in_rs_per_mwh=400,
        n1_price_in_rs_per_mwh=500,
        n2_price_in_rs_per_mwh=600,
        n3_price_in_rs_per_mwh=700,
        s1_price_in_rs_per_mwh=800,
        s2_price_in_rs_per_mwh=900,
        s3_price_in_rs_per_mwh=1000,
        w1_price_in_rs_per_mwh=1100,
        w2_price_in_rs_per_mwh=1200,
        w3_price_in_rs_per_mwh=1300,
        mcp_price_in_rs_per_mwh=1400,
    )
    with pytest.raises(ValueError):
        _convert_orm_model_to_pydantic_model(
            settlement_period_start_datetime, orm_instance, "invalid_market"
        )
