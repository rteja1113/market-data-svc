import datetime
import json

import click
from dateutil import parser

from src.common import logging_utils
from src.common.constants import MARKET_TZ
from src.common.enums import Markets
from src.database import Session
from src.marketdata.crud import MARKET_TO_DB_INSERTING_FN_MAP
from src.marketdata.schemas import (
    MARKETTYPE_TO_PRICE_PYD_MODEL_MAP,
    BasePointInTimePriceData,
)

session = Session()

logger = logging_utils.create_logger(__name__)


def _load_price_data_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r") as f:
        json_string = json.load(f)
    return json.loads(json_string)


def _convert_to_market_tz(datetime_string: str) -> datetime.datetime:
    numeric_tz_offset_datetime = parser.parse(datetime_string)
    market_tz_datetime = numeric_tz_offset_datetime.astimezone(MARKET_TZ)
    return market_tz_datetime


def _convert_dict_to_pyd(
    json_data: list[dict], price_enum: Markets
) -> list[BasePointInTimePriceData]:
    pit_pyd = []
    for row in json_data:
        market_tz_datetime = _convert_to_market_tz(
            row["settlement_period_start_datetime"]
        )
        row["settlement_period_start_datetime"] = market_tz_datetime
        pyd_class = MARKETTYPE_TO_PRICE_PYD_MODEL_MAP[price_enum]
        pyd_instance = pyd_class(**row)
        pit_pyd.append(pyd_instance)
    return pit_pyd  # type: ignore


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


@click.command()
@click.option("--json_path", type=str)
@click.option("--price_type", type=click.Choice(["DAM", "RTM"], case_sensitive=False))
def export_json_price_data_into_db(json_path: str, price_type: str) -> None:
    if _if_path_matches_price_type(json_path, price_type):
        price_pit_rows = _load_price_data_from_json(json_path)
        price_enum = Markets[price_type]
        pit_pyd_models = _convert_dict_to_pyd(price_pit_rows, price_enum)
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
