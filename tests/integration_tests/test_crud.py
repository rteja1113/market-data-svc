import datetime

import pytest

from src.common.enums import Markets
from src.common.models import TimeFrame
from src.marketdata.crud import (
    MARKET_TO_DB_GETTING_FN_MAP,
    MARKET_TO_DB_INSERTING_FN_MAP,
)
from src.marketdata.models import MARKETTYPE_TO_ORM_MAP


@pytest.mark.parametrize(
    "pyd_price_model, price_type",
    [("DAM", "DAM"), ("RTM", "RTM")],
    indirect=["pyd_price_model"],
)
def test_inserting_records(session, pyd_price_model, price_type):
    market_type_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(market_type_enum)
    db_model = row_inserting_fn(session, pyd_price_model)

    # check instance type
    assert isinstance(db_model, MARKETTYPE_TO_ORM_MAP.get(market_type_enum))
    # check by querying the migrations
    assert (
        session.query(MARKETTYPE_TO_ORM_MAP.get(market_type_enum)).first() == db_model
    )


@pytest.mark.parametrize(
    "pyd_price_model, price_type",
    [("DAM", "DAM"), ("RTM", "RTM")],
    indirect=["pyd_price_model"],
)
def test_getting_records(session, pyd_price_model, price_type):
    market_type_enum = Markets[price_type]
    row_getting_fn = MARKET_TO_DB_GETTING_FN_MAP.get(market_type_enum)
    time_frame = TimeFrame(
        start_datetime=datetime.datetime(2000, 1, 1),
        end_datetime=datetime.datetime(2050, 1, 1),
    )
    db_models = row_getting_fn(session, time_frame)

    # check instance type
    for db_model in db_models:
        assert isinstance(db_model, MARKETTYPE_TO_ORM_MAP.get(market_type_enum))
        # check by querying the migrations
