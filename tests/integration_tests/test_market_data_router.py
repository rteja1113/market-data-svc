import datetime

import pytest

from src.common.constants import MARKET_TZ
from src.common.enums import Markets
from src.common.models import TimeFrame
from src.marketdata.crud import (
    MARKET_TO_DB_GETTING_FN_MAP,
    MARKET_TO_DB_INSERTING_FN_MAP,
)


@pytest.mark.parametrize(
    "pyd_price_model, price_type",
    [("DAM", "DAM"), ("RTM", "RTM")],
    indirect=["pyd_price_model"],
)
def test_read_price_records(monkeypatch, client, session, pyd_price_model, price_type):
    monkeypatch.setattr("src.marketdata.router.get_db_session", lambda: session)

    market_type_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(market_type_enum)
    _ = row_inserting_fn(session, pyd_price_model)
    time_frame = TimeFrame(
        start_datetime=MARKET_TZ.localize(datetime.datetime(2000, 1, 1)),
        end_datetime=MARKET_TZ.localize(datetime.datetime(2050, 1, 1)),
    )

    reco = MARKET_TO_DB_GETTING_FN_MAP[market_type_enum](session, time_frame)
    print(reco[0].a1_price_in_rs_per_mwh)
    response = client.get(
        f"/marketdata/{price_type.lower()}?"
        f"start_datetime=2000-01-01 00:00:00&end_datetime=2050-01-02 00:00:00"
    )
    assert response.status_code == 200
    print(response.json())
