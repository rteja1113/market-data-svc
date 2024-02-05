import datetime

import pytest

from iex_app.api.crud.basic_crud import MARKET_TO_DB_INSERTING_FN_MAP
from iex_app.api.models.models import MARKETTYPE_TO_ORM_MAP
from iex_app.api.models.pydantic_models import MARKETTYPE_TO_PRICE_PYD_MODEL_MAP
from iex_app.common.constants import MARKET_TZ
from iex_app.common.enums import Markets


@pytest.fixture
def mock_datetime():
    return MARKET_TZ.localize(datetime.datetime(2022, 1, 1))


@pytest.fixture
def mock_prices():
    return [10.0] * 14


@pytest.fixture
def pyd_model(request, mock_datetime, mock_prices):
    pyd_class = MARKETTYPE_TO_PRICE_PYD_MODEL_MAP.get(Markets[request.param])
    return pyd_class(
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


@pytest.mark.parametrize(
    "pyd_model, price_type", [("DAM", "DAM"), ("RTM", "RTM")], indirect=["pyd_model"]
)
def test_inserting_records(session, pyd_model, price_type):
    market_type_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(market_type_enum)
    db_model = row_inserting_fn(session, pyd_model)
    assert isinstance(db_model, MARKETTYPE_TO_ORM_MAP.get(market_type_enum))


@pytest.mark.parametrize(
    "pyd_model, price_type", [("DAM", "DAM"), ("RTM", "RTM")], indirect=["pyd_model"]
)
def test_query_table_to_check_state(session, pyd_model, price_type):
    market_type_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(market_type_enum)
    db_model = row_inserting_fn(session, pyd_model)
    assert (
        session.query(MARKETTYPE_TO_ORM_MAP.get(market_type_enum)).first() == db_model
    )
