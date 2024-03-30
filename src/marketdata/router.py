import datetime
import functools
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from src.common import logging_utils
from src.common.enums import Markets
from src.common.utils import convert_naive_datetime_in_utc_to_ist
from src.database import Session  # noqa
from src.marketdata.crud import MARKET_TO_DB_GETTING_FN_MAP
from src.marketdata.router_utils import (
    _convert_orm_model_to_pydantic_model,
    _validate_and_convert_datetime_params,
)
from src.marketdata.schemas import BasePointInTimePriceData

logger = logging_utils.create_logger(__name__)

# Create a FastAPI app
router = APIRouter(prefix="/marketdata")


def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()


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
