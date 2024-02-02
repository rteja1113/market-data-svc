import datetime
import json
import logging
from typing import Callable, Union

import click
from dateutil import parser

from iex_app.api.crud.basic_crud import MARKET_TO_DB_INSERTING_FN_MAP
from iex_app.api.models.pydantic_models import (
    BasePointInTimePriceData,
    DAMPointInTimePriceData,
)
from iex_app.common.constants import MARKET_TZ
from iex_app.common.enums import Markets
from iex_app.db.core import Session

session = Session()

logger = logging.getLogger(__name__)


def _load_price_data_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r") as f:
        json_string = json.load(f)
    return json.loads(json_string)


def _convert_to_market_tz(datetime_string: str) -> datetime.datetime:
    numeric_tz_offset_datetime = parser.parse(datetime_string)
    market_tz_datetime = numeric_tz_offset_datetime.astimezone(MARKET_TZ)
    return market_tz_datetime


def _convert_dict_to_pyd(json_data: list[dict]) -> list[BasePointInTimePriceData]:
    pit_pyd = []
    for row in json_data:
        market_tz_datetime = _convert_to_market_tz(
            row["settlement_period_start_datetime"]
        )
        row["settlement_period_start_datetime"] = market_tz_datetime
        pit_pyd.append(DAMPointInTimePriceData(**row))
    return pit_pyd


def _if_path_matches_price_type(json_path: str, price_type: str) -> bool:
    if ("rtm" in json_path or "RTM" in json_path) and price_type == Markets.DAM.name:
        return click.confirm(
            "The json_path seems to point to RTM price json "
            "data and you are trying to add a record to"
            " DAM price table. Do you wish to continue?"
        )
    elif ("dam" in json_path or "DAM" in json_path) and price_type == Markets.RTM.name:
        return click.confirm(
            "The json_path seems to point to DAM price json "
            "data and you are trying to add a record to"
            " RTM price table. Do you wish to continue?"
        )
    return True


def _get_row_inserting_fn_from_price_type(price_type: str) -> Union[Callable | None]:
    price_enum = Markets[price_type]
    row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(price_enum)
    # if row_inserting_fn is None:
    #     raise ValueError(f"Invalid price type: {price_type}")
    return row_inserting_fn


@click.command()
@click.option("--json_path", type=str)
@click.option("--price_type", type=click.Choice(["DAM", "RTM"], case_sensitive=False))
def export_json_price_data_into_db(json_path: str, price_type: str) -> None:
    if _if_path_matches_price_type(json_path, price_type):
        price_pit_rows = _load_price_data_from_json(json_path)
        pit_pyd_models = _convert_dict_to_pyd(price_pit_rows)
        price_enum = Markets[price_type]
        row_inserting_fn = MARKET_TO_DB_INSERTING_FN_MAP.get(price_enum)
        if row_inserting_fn is None:
            raise ValueError(f"Invalid price type: {price_type}")
        try:
            for pit_pyd_model in pit_pyd_models:
                _ = row_inserting_fn(session, pit_pyd_model)
                logger.info(
                    f"{price_type} price Record created"
                    f" for {pit_pyd_model.settlement_period_start_datetime}"
                )
        except Exception as e:
            logger.exception(f"Error occurred while exporting data into db. Error: {e}")
        finally:
            session.close()
    return None


if __name__ == "__main__":
    export_json_price_data_into_db()
