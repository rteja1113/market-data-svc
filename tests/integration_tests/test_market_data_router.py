import pytest

from src.common.enums import Markets
from src.marketdata.crud import MARKET_TO_DB_INSERTING_FN_MAP


@pytest.fixture
def insert_row(session, pyd_price_model, price_type):
    market_type_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(market_type_enum)
    _ = row_inserting_fn(session, pyd_price_model)


@pytest.mark.parametrize(
    "pyd_price_model, price_type",
    [("DAM", "DAM"), ("RTM", "RTM")],
    indirect=["pyd_price_model"],
)
def test_read_price_records_valid_requests(
    client, session, pyd_price_model, price_type, insert_row
):
    response = client.get(
        f"/marketdata/{price_type.lower()}?"
        f"start_datetime=2000-01-01 00:00:00&end_datetime=2050-01-01 01:00:00"
    )
    assert response.status_code == 200
    expected_response = pyd_price_model.model_dump()
    actual_response = response.json()[0]
    assert actual_response == expected_response


@pytest.mark.parametrize(
    "pyd_price_model, price_type",
    [("DAM", "DAM"), ("RTM", "RTM")],
    indirect=["pyd_price_model"],
)
def test_read_price_records_invalid_requests(
    client, session, pyd_price_model, price_type, insert_row
):
    response = client.get(
        f"/marketdata/{price_type.lower()}?"
        f"start_datetime=2000-01-01T00:00:00&end_datetime=2050-01-01T01:00:00"
    )
    assert response.status_code == 400
