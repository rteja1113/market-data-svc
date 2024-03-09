import pytest
from click.testing import CliRunner

from src.common.enums import Markets
from src.marketdata.models import MARKETTYPE_TO_ORM_MAP
from src.migrations.manual.manual_data_migration import export_json_price_data_into_db


@pytest.mark.parametrize(
    "json_path, price_type",
    [
        ("./tests/integration_tests/json_data/dam_prices.json", "DAM"),
        ("./tests/integration_tests/json_data/rtm_prices.json", "RTM"),
    ],
)
def test_export_json_price_data_into_db(monkeypatch, session, json_path, price_type):
    monkeypatch.setattr("src.migrations.manual.manual_data_migration.session", session)
    runner = CliRunner()
    _ = runner.invoke(export_json_price_data_into_db, [json_path, price_type])
    market_type_enum = Markets[price_type]

    # check that the record was inserted into the migrations
    orm_instance = session.query(MARKETTYPE_TO_ORM_MAP.get(market_type_enum)).first()
    assert isinstance(orm_instance, MARKETTYPE_TO_ORM_MAP.get(market_type_enum))
