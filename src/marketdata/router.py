from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, Query
from starlette import status as StarletteStatus

from src.common import logging_utils
from src.common.utils import convert_timestamp_to_indian_datetime
from src.database import Session  # noqa
from src.marketdata.crud import get_dam_price_records, get_rtm_price_records
from src.marketdata.router_utils import convert_datetime_query_params_to_time_frame
from src.marketdata.schemas import DAMPointInTimePriceData, RTMPointInTimePriceData

logger = logging_utils.create_logger(__name__)

# Create a FastAPI app
router = APIRouter(prefix="/marketdata")


def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()


StartTimeQueryParameter = Annotated[
    str,
    Query(
        alias="start_datetime",
        description="Start datetime in ISO format(Ex: 2021-01-01 00:00:00)",
    ),
]
EndTimeQueryParameter = Annotated[
    str,
    Query(
        alias="end_datetime",
        description="end datetime in ISO format(Ex: 2021-01-01 00:00:00)",
    ),
]
DbDepends = Annotated[Session, Depends(get_db_session)]


@router.get("/dam")
def read_dam_price_records(
    start_datetime_str: StartTimeQueryParameter,
    end_datetime_str: EndTimeQueryParameter,
    db_session: DbDepends,
) -> list[DAMPointInTimePriceData]:
    try:
        time_frame = convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
    except ValueError as e:
        logger.error(f"Error while converting datetime query params: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format",
        )
    try:
        price_records = get_dam_price_records(db_session, time_frame)
        return [
            DAMPointInTimePriceData(
                settlement_period_start_datetime=convert_timestamp_to_indian_datetime(
                    price_record.settlement_period_start_timestamp
                ),
                **price_record.__dict__,
            )
            for price_record in price_records
        ]
    except Exception as e:
        logger.error(f"Error while fetching DAM price records: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while fetching DAM price records",
        )


@router.get("/rtm")
def read_rtm_price_records(
    start_datetime_str: StartTimeQueryParameter,
    end_datetime_str: EndTimeQueryParameter,
    db_session: DbDepends,
) -> list[RTMPointInTimePriceData]:
    try:
        time_frame = convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
    except ValueError as e:
        logger.error(f"Error while converting datetime query params: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format",
        )

    try:
        price_records = get_rtm_price_records(db_session, time_frame)
        return [
            RTMPointInTimePriceData(
                settlement_period_start_datetime=convert_timestamp_to_indian_datetime(
                    price_record.settlement_period_start_timestamp
                ),
                **price_record.__dict__,
            )
            for price_record in price_records
        ]
    except Exception as e:
        logger.error(f"Error while fetching RTM price records: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while fetching RTM price records",
        )
