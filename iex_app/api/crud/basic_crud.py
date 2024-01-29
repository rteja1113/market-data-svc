from iex_app.api.models.models import (
    DAMPointInTimePriceDataDb,
    RTMPointInTimePriceDataDb,
)
from iex_app.api.models.pydantic_models import (
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)
from iex_app.db.core import Session


def create_dam_record(
    db_session: Session, dam_pit_data: DAMPointInTimePriceData
) -> DAMPointInTimePriceDataDb:
    """
    Create a record in the database for the DAM price
    :param db_session: The database session
    :param dam_pit_data: The DAM price pydantic model instance
    :return: None
    """

    dam_record = DAMPointInTimePriceDataDb(**dam_pit_data.model_dump())
    db_session.add(dam_record)
    db_session.commit()
    db_session.refresh(dam_pit_data)
    return dam_record


def create_rtm_record(
    db_session: Session, rtm_pit_data: RTMPointInTimePriceData
) -> RTMPointInTimePriceDataDb:
    """
    Create a record in the database for the RTM price
    :param db_session: The database session
    :param rtm_pit_data: The RTM price pydantic model instance
    :return: None
    """

    rtm_record = RTMPointInTimePriceDataDb(**rtm_pit_data.model_dump())
    db_session.add(rtm_record)
    db_session.commit()
    db_session.refresh(rtm_pit_data)
    return rtm_record
