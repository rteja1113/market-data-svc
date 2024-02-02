import logging

import sqlalchemy

from iex_app.api.models.models import (
    BasePointInTimePriceDataDb,
    DAMPointInTimePriceDataDb,
    RTMPointInTimePriceDataDb,
)
from iex_app.api.models.pydantic_models import (
    BasePointInTimePriceData,
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)
from iex_app.db.core import Session

logger = logging.getLogger(__name__)


def _create_price_record(
    db_session: Session,
    pit_data: BasePointInTimePriceData,
    db_price_model: sqlalchemy.orm.decl_api.DeclarativeMeta,
) -> BasePointInTimePriceDataDb:
    existing_record = (
        db_session.query(db_price_model)
        .filter(
            db_price_model.settlement_period_start_datetime
            == pit_data.settlement_period_start_datetime
        )
        .first()
    )

    if existing_record is not None:
        logger.info(
            f"Record already exists for {pit_data.settlement_period_start_datetime}"
        )
        return existing_record

    pit_record = db_price_model(**pit_data.model_dump())
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
