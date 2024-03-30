import datetime

from fastapi import HTTPException
from starlette import status

from src.common.constants import MARKET_TZ
from src.common.enums import Markets
from src.common.models import TimeFrame
from src.marketdata.models import (
    BasePointInTimePriceDataDb,
    DAMPointInTimePriceDataDb,
    RTMPointInTimePriceDataDb,
)
from src.marketdata.schemas import (
    BasePointInTimePriceData,
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)


def _convert_string_to_datetime(datetime_string: str) -> datetime.datetime:
    return MARKET_TZ.localize(
        datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    )


def _validate_and_convert_datetime_params(
    start_datetime_str: str, end_datetime_str: str
) -> TimeFrame:
    try:
        start_datetime = _convert_string_to_datetime(start_datetime_str)
        end_datetime = _convert_string_to_datetime(end_datetime_str)
        if start_datetime > end_datetime:
            raise ValueError("start_datetime should be less than end_datetime")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return TimeFrame(start_datetime=start_datetime, end_datetime=end_datetime)


def _convert_orm_model_to_pydantic_model(
    settlement_period_start_datetime: datetime.datetime,
    orm_instance: BasePointInTimePriceDataDb,
    market_type: Markets,
) -> BasePointInTimePriceData:
    if market_type == Markets.DAM:
        if not isinstance(orm_instance, DAMPointInTimePriceDataDb):
            raise ValueError(
                f"Invalid ORM instance type for DAM market: {type(orm_instance)}"
            )
        price_pyd_model_class = DAMPointInTimePriceData
    elif market_type == Markets.RTM:
        if not isinstance(orm_instance, RTMPointInTimePriceDataDb):
            raise ValueError(
                f"Invalid ORM instance type for RTM market: {type(orm_instance)}"
            )
        price_pyd_model_class = RTMPointInTimePriceData
    else:
        raise ValueError(f"Invalid market type: {market_type}")

    price_pyd_model = price_pyd_model_class(
        settlement_period_start_datetime=settlement_period_start_datetime,
        a1_price_in_rs_per_mwh=orm_instance.a1_price_in_rs_per_mwh,
        a2_price_in_rs_per_mwh=orm_instance.a2_price_in_rs_per_mwh,
        e1_price_in_rs_per_mwh=orm_instance.e1_price_in_rs_per_mwh,
        e2_price_in_rs_per_mwh=orm_instance.e2_price_in_rs_per_mwh,
        n1_price_in_rs_per_mwh=orm_instance.n1_price_in_rs_per_mwh,
        n2_price_in_rs_per_mwh=orm_instance.n2_price_in_rs_per_mwh,
        n3_price_in_rs_per_mwh=orm_instance.n3_price_in_rs_per_mwh,
        s1_price_in_rs_per_mwh=orm_instance.s1_price_in_rs_per_mwh,
        s2_price_in_rs_per_mwh=orm_instance.s2_price_in_rs_per_mwh,
        s3_price_in_rs_per_mwh=orm_instance.s3_price_in_rs_per_mwh,
        w1_price_in_rs_per_mwh=orm_instance.w1_price_in_rs_per_mwh,
        w2_price_in_rs_per_mwh=orm_instance.w2_price_in_rs_per_mwh,
        w3_price_in_rs_per_mwh=orm_instance.w3_price_in_rs_per_mwh,
        mcp_price_in_rs_per_mwh=orm_instance.mcp_price_in_rs_per_mwh,
    )
    return price_pyd_model
