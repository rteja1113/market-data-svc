import datetime
import json
import logging

import click
from dateutil import parser

from iex_app.api.crud.basic_crud import create_dam_price_record
from iex_app.api.models.pydantic_models import DAMPointInTimePriceData
from iex_app.common.constants import MARKET_TZ
from iex_app.db.core import Session

session = Session()

logger = logging.getLogger(__name__)


def load_dam_data_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r") as f:
        json_string = json.load(f)
    return json.loads(json_string)


def _convert_to_market_tz(datetime_string: str) -> datetime.datetime:
    numeric_tz_offset_datetime = parser.parse(datetime_string)
    market_tz_datetime = numeric_tz_offset_datetime.astimezone(MARKET_TZ)
    return market_tz_datetime


def _convert_dict_to_pyd(json_data: list[dict]) -> list[DAMPointInTimePriceData]:
    dam_pit_pyd = []
    for row in json_data:
        market_tz_datetime = _convert_to_market_tz(
            row["settlement_period_start_datetime"]
        )
        row["settlement_period_start_datetime"] = market_tz_datetime
        dam_pit_pyd.append(DAMPointInTimePriceData(**row))
    return dam_pit_pyd


@click.command()
@click.option("--json_path")
def export_raw_dam_data_into_db(json_path) -> None:
    dam_pit_rows = load_dam_data_from_json(json_path)
    dam_pit_pyd_models = _convert_dict_to_pyd(dam_pit_rows)
    try:
        for dam_pit_data in dam_pit_pyd_models:
            _ = create_dam_price_record(session, dam_pit_data)
            logger.info(
                f"DAM price Record created"
                f" for {dam_pit_data.settlement_period_start_datetime}"
            )
    except Exception as e:
        logger.exception(f"Error occurred while exporting data into db. Error: {e}")
    finally:
        session.close()
    return None


if __name__ == "__main__":
    export_raw_dam_data_into_db()
