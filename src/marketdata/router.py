import datetime
from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, Query
from starlette import status as StarletteStatus

from src.common import logging_utils
from src.common.utils import convert_naive_datetime_in_utc_to_ist
from src.database import Session  # noqa
from src.marketdata.crud import get_dam_price_records, get_rtm_price_records
from src.marketdata.router_utils import _convert_datetime_query_params_to_time_frame
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


@router.get("/dam")
def read_dam_price_records(
    start_datetime_str: Annotated[str, Query(alias="start_datetime")],
    end_datetime_str: Annotated[str, Query(alias="end_datetime")],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> list[DAMPointInTimePriceData]:
    """
    Fetches the dam price records for the given time frame
    """
    try:
        time_frame = _convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
    except ValueError as e:
        logger.error(f"Error while converting datetime query params: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format",
        )

    price_records = get_dam_price_records(db_session, time_frame)

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
    db_session: Annotated[Session, Depends(get_db_session)],
) -> list[RTMPointInTimePriceData]:
    """
    Fetches rtm price records for the given time frame
    """
    try:
        time_frame = _convert_datetime_query_params_to_time_frame(
            start_datetime_str, end_datetime_str
        )
    except ValueError as e:
        logger.error(f"Error while converting datetime query params: {e}")
        raise fastapi.HTTPException(
            status_code=StarletteStatus.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format",
        )

    price_records = get_rtm_price_records(db_session, time_frame)

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
