import datetime

import pytest

from iex_app.api.crud.basic_crud import create_dam_price_record, create_rtm_price_record
from iex_app.api.models.models import (
    DAMPointInTimePriceDataDb,
    RTMPointInTimePriceDataDb,
)
from iex_app.api.models.pydantic_models import (
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)
from iex_app.common.constants import MARKET_TZ


@pytest.fixture
def mock_datetime():
    return MARKET_TZ.localize(datetime.datetime(2022, 1, 1))


@pytest.fixture
def mock_prices():
    return [10.0] * 14


@pytest.fixture
def mock_dam_price_data(mock_datetime, mock_prices):
    return DAMPointInTimePriceData(
        settlement_period_start_datetime=mock_datetime,
        a1_price_in_rs_per_mwh=mock_prices[0],
        a2_price_in_rs_per_mwh=mock_prices[1],
        e1_price_in_rs_per_mwh=mock_prices[2],
        e2_price_in_rs_per_mwh=mock_prices[3],
        n1_price_in_rs_per_mwh=mock_prices[4],
        n2_price_in_rs_per_mwh=mock_prices[5],
        n3_price_in_rs_per_mwh=mock_prices[6],
        s1_price_in_rs_per_mwh=mock_prices[7],
        s2_price_in_rs_per_mwh=mock_prices[8],
        s3_price_in_rs_per_mwh=mock_prices[9],
        w1_price_in_rs_per_mwh=mock_prices[10],
        w2_price_in_rs_per_mwh=mock_prices[11],
        w3_price_in_rs_per_mwh=mock_prices[12],
        mcp_price_in_rs_per_mwh=mock_prices[13],
    )


@pytest.fixture
def mock_rtm_price_data(mock_datetime, mock_prices):
    return RTMPointInTimePriceData(
        settlement_period_start_datetime=mock_datetime,
        a1_price_in_rs_per_mwh=mock_prices[0],
        a2_price_in_rs_per_mwh=mock_prices[1],
        e1_price_in_rs_per_mwh=mock_prices[2],
        e2_price_in_rs_per_mwh=mock_prices[3],
        n1_price_in_rs_per_mwh=mock_prices[4],
        n2_price_in_rs_per_mwh=mock_prices[5],
        n3_price_in_rs_per_mwh=mock_prices[6],
        s1_price_in_rs_per_mwh=mock_prices[7],
        s2_price_in_rs_per_mwh=mock_prices[8],
        s3_price_in_rs_per_mwh=mock_prices[9],
        w1_price_in_rs_per_mwh=mock_prices[10],
        w2_price_in_rs_per_mwh=mock_prices[11],
        w3_price_in_rs_per_mwh=mock_prices[12],
        mcp_price_in_rs_per_mwh=mock_prices[13],
    )


def test_create_dam_price_record(session, mock_dam_price_data):
    dam_record = create_dam_price_record(session, mock_dam_price_data)
    assert isinstance(dam_record, DAMPointInTimePriceDataDb)
    assert dam_record.mcp_price_in_rs_per_mwh == 10.0
    assert (
        dam_record.settlement_period_start_datetime
        == mock_dam_price_data.settlement_period_start_datetime
    )


def test_query_dam_table(session, mock_dam_price_data):
    dam_record = create_dam_price_record(session, mock_dam_price_data)
    assert session.query(DAMPointInTimePriceDataDb).first() == dam_record


def test_create_rtm_price_record(session, mock_rtm_price_data):
    rtm_record = create_rtm_price_record(session, mock_rtm_price_data)
    assert isinstance(rtm_record, RTMPointInTimePriceDataDb)
    assert rtm_record.mcp_price_in_rs_per_mwh == 10.0
    assert (
        rtm_record.settlement_period_start_datetime
        == mock_rtm_price_data.settlement_period_start_datetime
    )


def test_query_rtm_table(session, mock_rtm_price_data):
    rtm_record = create_rtm_price_record(session, mock_rtm_price_data)
    assert session.query(RTMPointInTimePriceDataDb).first() == rtm_record
