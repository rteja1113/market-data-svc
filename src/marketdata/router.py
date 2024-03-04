import datetime
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.common.constants import MARKET_TZ
from src.common.models import TimeFrame
from src.common.utils import convert_naive_datetime_in_utc_to_ist
from src.database import Session  # noqa
from src.marketdata.crud import get_dam_price_records, get_rtm_price_records
from src.marketdata.schemas import DAMPointInTimePriceData, RTMPointInTimePriceData

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
router = APIRouter(prefix="/marketdata")


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


@router.get("/dam")
def read_dam_price_records(
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db: Session = Depends(get_db),
) -> list[DAMPointInTimePriceData]:
    """
    Fetches the DAM price records for the given time frame
    """
    time_frame = _validate_and_convert_datetime_params(
        start_datetime_str, end_datetime_str
    )

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


@router.get("/rtm")
def read_rtm_price_records(
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db: Session = Depends(get_db),
) -> list[RTMPointInTimePriceData]:
    """
    Fetches the RTM price records for the given time frame
    """
    time_frame = _validate_and_convert_datetime_params(
        start_datetime_str, end_datetime_str
    )
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
