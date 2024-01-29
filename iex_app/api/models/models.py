from sqlalchemy import Column, DateTime, Float, Integer, String

from iex_app.db.core import Base


class BasePointInTimePriceDataDb(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    settlement_period_start_datetime = Column(DateTime(timezone=True), unique=True)
    a1_price_in_rs_per_mwh = Column(Float)
    a2_price_in_rs_per_mwh = Column(Float)
    e1_price_in_rs_per_mwh = Column(Float)
    e2_price_in_rs_per_mwh = Column(Float)
    n1_price_in_rs_per_mwh = Column(Float)
    n2_price_in_rs_per_mwh = Column(Float)
    n3_price_in_rs_per_mwh = Column(Float)
    s1_price_in_rs_per_mwh = Column(Float)
    s2_price_in_rs_per_mwh = Column(Float)
    s3_price_in_rs_per_mwh = Column(Float)
    w1_price_in_rs_per_mwh = Column(Float)
    w2_price_in_rs_per_mwh = Column(Float)
    w3_price_in_rs_per_mwh = Column(Float)
    mcp_price_in_rs_per_mwh = Column(Float)


class DAMPointInTimePriceDataDb(BasePointInTimePriceDataDb):
    __tablename__ = "dam_prices"


class RTMPointInTimePriceDataDb(BasePointInTimePriceDataDb):
    __tablename__ = "rtm_prices"
    session_id = Column(String)
