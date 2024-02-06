import pytest

from iex_app.api.crud.basic_crud import MARKET_TO_DB_INSERTING_FN_MAP
from iex_app.api.models.models import MARKETTYPE_TO_ORM_MAP
from iex_app.common.enums import Markets


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
    # check by querying the db
    assert (
        session.query(MARKETTYPE_TO_ORM_MAP.get(market_type_enum)).first() == db_model
    )
