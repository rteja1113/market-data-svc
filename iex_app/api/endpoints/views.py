import datetime
import logging
from typing import Annotated

import pydantic
import uvicorn
from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from iex_app.api.crud.basic_crud import get_dam_price_records, get_rtm_price_records
from iex_app.api.models.pydantic_models import (
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)
from iex_app.common.constants import MARKET_TZ
from iex_app.common.models import TimeFrame
from iex_app.common.utils import convert_naive_datetime_in_utc_to_ist
from iex_app.db.core import Session  # noqa

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

# Create a FastAPI app
app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def _convert_string_to_datetime(datetime_string: str) -> datetime.datetime:
    return MARKET_TZ.localize(
        datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    )


@app.get("/historicmarketdata/dam/")
def read_dam_price_records(
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db: Session = Depends(get_db),
) -> list[DAMPointInTimePriceData]:
    try:
        start_datetime = _convert_string_to_datetime(start_datetime_str)
    except ValueError:
        logger.error(f"Invalid start_datetime: {start_datetime}")
        return []

    try:
        end_datetime = _convert_string_to_datetime(end_datetime_str)
    except ValueError:
        logger.error(f"Invalid end_datetime: {end_datetime}")
        return []

    try:
        time_frame = TimeFrame(start_datetime=start_datetime, end_datetime=end_datetime)
    except pydantic.ValidationError as e:
        logger.error(f"Invalid time_frame: {e}")
        return []

    price_records = get_dam_price_records(db, time_frame)

    price_pyd_models = []
    for price_record in price_records:
        ist_dt = convert_naive_datetime_in_utc_to_ist(
            datetime.datetime.utcfromtimestamp(
                price_record.settlement_period_start_timestamp
            )
        )
        price_pyd_model = DAMPointInTimePriceData(
            settlement_period_start_datetime=ist_dt,
            a1_price_in_rs_per_mwh=price_record.a1_price_in_rs_per_mwh,
            a2_price_in_rs_per_mwh=price_record.a2_price_in_rs_per_mwh,
            e1_price_in_rs_per_mwh=price_record.e1_price_in_rs_per_mwh,
            e2_price_in_rs_per_mwh=price_record.e2_price_in_rs_per_mwh,
            n1_price_in_rs_per_mwh=price_record.n1_price_in_rs_per_mwh,
            n2_price_in_rs_per_mwh=price_record.n2_price_in_rs_per_mwh,
            n3_price_in_rs_per_mwh=price_record.n3_price_in_rs_per_mwh,
            s1_price_in_rs_per_mwh=price_record.s1_price_in_rs_per_mwh,
            s2_price_in_rs_per_mwh=price_record.s2_price_in_rs_per_mwh,
            s3_price_in_rs_per_mwh=price_record.s3_price_in_rs_per_mwh,
            w1_price_in_rs_per_mwh=price_record.w1_price_in_rs_per_mwh,
            w2_price_in_rs_per_mwh=price_record.w2_price_in_rs_per_mwh,
            w3_price_in_rs_per_mwh=price_record.w3_price_in_rs_per_mwh,
            mcp_price_in_rs_per_mwh=price_record.mcp_price_in_rs_per_mwh,
        )
        price_pyd_models.append(price_pyd_model)
    return price_pyd_models


@app.get("/historicmarketdata/rtm/")
def read_rtm_price_records(
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db: Session = Depends(get_db),
) -> list[RTMPointInTimePriceData]:
    try:
        start_datetime = _convert_string_to_datetime(start_datetime_str)
    except ValueError:
        logger.error(f"Invalid start_datetime: {start_datetime}")
        return []

    try:
        end_datetime = _convert_string_to_datetime(end_datetime_str)
    except ValueError:
        logger.error(f"Invalid end_datetime: {end_datetime}")
        return []

    try:
        time_frame = TimeFrame(start_datetime=start_datetime, end_datetime=end_datetime)
    except pydantic.ValidationError as e:
        logger.error(f"Invalid time_frame: {e}")
        return []

    price_records = get_rtm_price_records(db, time_frame)
    price_pyd_models = []
    for price_record in price_records:
        ist_dt = convert_naive_datetime_in_utc_to_ist(
            datetime.datetime.utcfromtimestamp(
                price_record.settlement_period_start_timestamp
            )
        )
        price_pyd_model = RTMPointInTimePriceData(
            settlement_period_start_datetime=ist_dt,
            a1_price_in_rs_per_mwh=price_record.a1_price_in_rs_per_mwh,
            a2_price_in_rs_per_mwh=price_record.a2_price_in_rs_per_mwh,
            e1_price_in_rs_per_mwh=price_record.e1_price_in_rs_per_mwh,
            e2_price_in_rs_per_mwh=price_record.e2_price_in_rs_per_mwh,
            n1_price_in_rs_per_mwh=price_record.n1_price_in_rs_per_mwh,
            n2_price_in_rs_per_mwh=price_record.n2_price_in_rs_per_mwh,
            n3_price_in_rs_per_mwh=price_record.n3_price_in_rs_per_mwh,
            s1_price_in_rs_per_mwh=price_record.s1_price_in_rs_per_mwh,
            s2_price_in_rs_per_mwh=price_record.s2_price_in_rs_per_mwh,
            s3_price_in_rs_per_mwh=price_record.s3_price_in_rs_per_mwh,
            w1_price_in_rs_per_mwh=price_record.w1_price_in_rs_per_mwh,
            w2_price_in_rs_per_mwh=price_record.w2_price_in_rs_per_mwh,
            w3_price_in_rs_per_mwh=price_record.w3_price_in_rs_per_mwh,
            mcp_price_in_rs_per_mwh=price_record.mcp_price_in_rs_per_mwh,
        )
        price_pyd_models.append(price_pyd_model)
    return price_pyd_models


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
