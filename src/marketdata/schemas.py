from __future__ import annotations

import abc
import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from src.common.enums import Markets


class BasePointInTimePriceData(BaseModel, abc.ABC):
    """
    A base class for price. This class describes
    the price data for a single point in time for all
    the zones along with the market clearing price in units rs/MWh
    """

    model_config = ConfigDict(frozen=True)
    settlement_period_start_datetime: datetime.datetime
    a1_price_in_rs_per_mwh: float | None = None
    a2_price_in_rs_per_mwh: float | None = None
    e1_price_in_rs_per_mwh: float | None = None
    e2_price_in_rs_per_mwh: float | None = None
    n1_price_in_rs_per_mwh: float | None = None
    n2_price_in_rs_per_mwh: float | None = None
    n3_price_in_rs_per_mwh: float | None = None
    s1_price_in_rs_per_mwh: float | None = None
    s2_price_in_rs_per_mwh: float | None = None
    s3_price_in_rs_per_mwh: float | None = None
    w1_price_in_rs_per_mwh: float | None = None
    w2_price_in_rs_per_mwh: float | None = None
    w3_price_in_rs_per_mwh: float | None = None
    mcp_price_in_rs_per_mwh: float | None = None

    @field_serializer("settlement_period_start_datetime")
    def serialize_settlement_period_start_datetime(self, value):
        return value.isoformat()


class DAMPointInTimePriceData(BasePointInTimePriceData):
    """
    A class that describes the day ahead market price  for a
    single point in time for all the state zones along with the
    clearing price
    """

    pass


class RTMPointInTimePriceData(BasePointInTimePriceData):
    """
    A class that describes the real time market price
    for a single point in time for all the state zones
    along with the clearing price
    """

    session_id: str | None = None


MARKETTYPE_TO_PRICE_PYD_MODEL_MAP = {
    Markets.DAM: DAMPointInTimePriceData,
    Markets.RTM: RTMPointInTimePriceData,
}
