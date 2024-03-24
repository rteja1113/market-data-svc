import datetime
import functools
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.common import logging_utils
from src.common.constants import MARKET_TZ
from src.common.enums import Markets
from src.common.models import TimeFrame
from src.common.utils import convert_naive_datetime_in_utc_to_ist
from src.database import Session  # noqa
from src.marketdata.crud import MARKET_TO_DB_GETTING_FN_MAP
from src.marketdata.models import BasePointInTimePriceDataDb
from src.marketdata.schemas import (
    BasePointInTimePriceData,
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)

logger = logging_utils.create_logger(__name__)

# Create a FastAPI app
router = APIRouter(prefix="/marketdata")


def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()


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
        price_pyd_model_class = DAMPointInTimePriceData
    elif market_type == Markets.RTM:
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


@router.get("/{market_type}")
def read_price_records(
    market_type: Annotated[Markets, Path(description="Market type (dam or rtm)")],
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> list[BasePointInTimePriceData]:
    """
    Fetches the price records for the given time frame and market type
    """
    time_frame = _validate_and_convert_datetime_params(
        start_datetime_str, end_datetime_str
    )

    price_records = MARKET_TO_DB_GETTING_FN_MAP[market_type](db_session, time_frame)
    orm_to_pydantic_converter = functools.partial(
        _convert_orm_model_to_pydantic_model, market_type=market_type
    )
    price_pyd_models = []
    for price_record in price_records:
        ist_dt = convert_naive_datetime_in_utc_to_ist(
            datetime.datetime.utcfromtimestamp(
                price_record.settlement_period_start_timestamp
            )
        )
        price_pyd_model = orm_to_pydantic_converter(
            settlement_period_start_datetime=ist_dt, orm_instance=price_record
        )
        price_pyd_models.append(price_pyd_model)
    return price_pyd_models
