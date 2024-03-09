import logging

import sqlalchemy

from src.common.enums import Markets
from src.common.models import TimeFrame
from src.database import Session
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


def _create_price_record(
    db_session: Session,
    pit_data: BasePointInTimePriceData,
    db_price_model: sqlalchemy.orm.decl_api.DeclarativeMeta,
) -> BasePointInTimePriceDataDb:
    existing_record = (
        db_session.query(db_price_model)
        .filter(
            db_price_model.settlement_period_start_timestamp
            == pit_data.settlement_period_start_datetime.timestamp()
        )
        .first()
    )

    if existing_record is not None:
        logger.info(
            f"Record already exists for {pit_data.settlement_period_start_datetime}"
        )
        return existing_record
    pyd_model_dump = pit_data.model_dump()
    pyd_model_dump[
        "settlement_period_start_timestamp"
    ] = pit_data.settlement_period_start_datetime.timestamp()
    pyd_model_dump.pop("settlement_period_start_datetime")
    pit_record = db_price_model(**pyd_model_dump)
    db_session.add(pit_record)
    db_session.commit()
    db_session.refresh(pit_record)
    return pit_record


def create_dam_price_record(
    db_session: Session, dam_pit_data: DAMPointInTimePriceData
) -> DAMPointInTimePriceDataDb:
    return _create_price_record(db_session, dam_pit_data, DAMPointInTimePriceDataDb)


def create_rtm_price_record(
    db_session: Session, rtm_pit_data: RTMPointInTimePriceData
) -> RTMPointInTimePriceDataDb:
    return _create_price_record(db_session, rtm_pit_data, RTMPointInTimePriceDataDb)


def _get_price_records(
    db_session: Session,
    time_frame: TimeFrame,
    db_price_model: sqlalchemy.orm.decl_api.DeclarativeMeta,
) -> list[BasePointInTimePriceDataDb]:
    records = (
        db_session.query(db_price_model)
        .filter(
            db_price_model.settlement_period_start_timestamp.between(
                time_frame.start_datetime.timestamp(),
                time_frame.end_datetime.timestamp(),
            )
        )
        .all()
    )
    return records


def get_dam_price_records(
    db_session: Session, time_frame: TimeFrame
) -> list[DAMPointInTimePriceDataDb]:
    return _get_price_records(db_session, time_frame, DAMPointInTimePriceDataDb)


def get_rtm_price_records(
    db_session: Session, time_frame: TimeFrame
) -> list[RTMPointInTimePriceDataDb]:
    return _get_price_records(db_session, time_frame, RTMPointInTimePriceDataDb)


MARKET_TO_DB_INSERTING_FN_MAP = {
    Markets.DAM: create_dam_price_record,
    Markets.RTM: create_rtm_price_record,
}
