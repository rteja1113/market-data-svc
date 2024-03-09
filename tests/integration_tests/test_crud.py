import pytest

from src.common.enums import Markets
from src.marketdata.crud import MARKET_TO_DB_INSERTING_FN_MAP
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
