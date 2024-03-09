from __future__ import annotations

import abc
import datetime
import logging

import bs4

from src.common.constants import MARKET_TZ, NUM_TIME_STEPS_IN_HOUR
from src.marketdata.schemas import (
    BasePointInTimePriceData,
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)

logger = logging.getLogger(__name__)


class BaseHtmlParsingEngine(abc.ABC):
    PRICE_TABLE_NUM_COLS = 1
    PRICE_COLUMN_OFFSET = 2
    DATA_ROW_OFFSET = 2

    @classmethod
    @abc.abstractmethod
    def _determine_column_offset_by_row_id(cls, row_id: int) -> int:
        """
        Determines the offset of the columns in the row based on the row id.
        Unfortunately, every row has a different number of columns,
        so we need to determine the offset based on the row id.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _parse_row_data_to_pydantic(
        cls,
        row: bs4.element.Tag,
        trading_day_beginning_datetime: datetime.datetime,
        row_id: int,
    ) -> BasePointInTimePriceData:
        """
        Parses the price table row and returns a BasePointInTimePriceData object.
        Inheritors should probably use _parse_row to do the actual parsing
        """
        pass

    @classmethod
    def _parse_row(
        cls,
        row: bs4.element.Tag,
        trading_day_beginning_datetime: datetime.datetime,
        row_id: int,
    ) -> tuple[datetime.datetime, list[float | None]]:
        """
        Parses the data_archived from a row in the price table.
        Returns a tuple of the datetime and the energy prices for
        all zones for that datetime.
        """
        cells = row.find_all("td")
        column_offset = cls._determine_column_offset_by_row_id(row_id)
        price_datetime = (
            trading_day_beginning_datetime
            + cls._parse_time_interval_from_cell(
                cells[1 + column_offset],
            )
        )
        energy_prices: list[float | None] = []
        for col_id in range(cls.PRICE_COLUMN_OFFSET + column_offset, len(cells)):
            cell = cells[col_id]
            try:
                price_val = float(cell.text.strip())
            except Exception as e:
                logger.error("Error parsing price value from cell", exc_info=e)
                price_val = float("nan")
            energy_prices.append(price_val)

        return price_datetime, energy_prices

    @staticmethod
    def _parse_time_interval_from_cell(cell: bs4.element.Tag) -> datetime.timedelta:
        """
        The cell has text in the format "HH:MM - HH:MM" where the first time is
        the start of the time interval and the second
        :param cell:
        :return:
        """
        cell_text = cell.text.strip()
        start_hour_and_min, end_hour_and_min = cell_text.split(" - ")
        hour = int(start_hour_and_min.split(":")[0])
        minute = int(start_hour_and_min.split(":")[1])
        return datetime.timedelta(hours=hour, minutes=minute)

    @staticmethod
    def _is_hour_mark(row_id: int) -> bool:
        return (row_id - 2) % NUM_TIME_STEPS_IN_HOUR == 0

    @staticmethod
    def _is_price_table_present(page: bs4.BeautifulSoup, num_table_cols: int) -> bool:
        tables = page.find_all("table")
        for table in tables:
            if int(table.get("cols", 0)) == num_table_cols:
                return True
        return False

    @classmethod
    def _get_price_table_from_page(cls, page: bs4.BeautifulSoup) -> bs4.element.Tag:
        """
        Gets the price table from the page. The price table is the table
        with DAM_TABLE_NUM_COLS columns
        """
        if cls._is_price_table_present(page, cls.PRICE_TABLE_NUM_COLS):
            tables = page.find_all("table")
            for table in tables:
                if int(table.get("cols", 0)) == cls.PRICE_TABLE_NUM_COLS:
                    price_table: bs4.element.Tag = table
                    return price_table
        else:
            raise ValueError(
                "page does not contain a table with the expected number of columns",
            )

    @staticmethod
    def _get_trading_day_start_datetime_from_price_table(
        price_table: bs4.element.Tag,
    ) -> datetime.datetime:
        """
        Gets the datetime of the start of the trading day from the
        price table. It can be found in row 2
        """
        all_rows: bs4.element.ResultSet = price_table.find_all("tr")
        row_2 = all_rows[2]
        cells = row_2.find_all("td")
        day_beginning_datetime = datetime.datetime.strptime(
            cells[1].text.strip(),
            "%d-%m-%Y",
        )
        day_beginning_datetime = MARKET_TZ.localize(day_beginning_datetime)
        return day_beginning_datetime

    @classmethod
    def _parse_all_rows_from_price_table(
        cls,
        price_table: bs4.element.Tag,
        trading_day_beginning_datetime: datetime.datetime,
    ) -> list[BasePointInTimePriceData]:
        """
        Parses all rows from the price table and returns a list of
        BasePointInTimePriceData objects
        """

        # initialize data_archived structures
        price_data: list[BasePointInTimePriceData] = []

        # get all rows
        rows: bs4.element.ResultSet = price_table.find_all("tr")
        num_rows = len(rows)

        # parse rows
        for row_id in range(cls.DATA_ROW_OFFSET, num_rows):
            curr_pit_data = cls._parse_row_data_to_pydantic(
                rows[row_id],
                trading_day_beginning_datetime,
                row_id,
            )
            price_data.append(curr_pit_data)
        return price_data

    @classmethod
    def parse_doc_to_price_data(
        cls, html_content: str
    ) -> list[BasePointInTimePriceData]:
        page_soup = bs4.BeautifulSoup(html_content, "html.parser")
        price_table: bs4.element.Tag = cls._get_price_table_from_page(page_soup)
        trading_day_beginning_datetime = (
            cls._get_trading_day_start_datetime_from_price_table(
                price_table,
            )
        )
        price_data = cls._parse_all_rows_from_price_table(
            price_table,
            trading_day_beginning_datetime,
        )
        return price_data


class DAMHtmlParsingEngine(BaseHtmlParsingEngine):
    DATA_ROW_OFFSET = 2
    PRICE_COLUMN_OFFSET = 2
    PRICE_TABLE_NUM_COLS = 18

    @classmethod
    def _determine_column_offset_by_row_id(cls, row_id: int) -> int:
        """
        Determines the offset of the columns in the row based on the row id.
        Unfortunately, every row has a different number of columns, so we need
        to determine the offset based on the row id.
        """
        if row_id == 2:
            return 2
        if cls._is_hour_mark(row_id):
            return 1
        else:
            return 0

    @classmethod
    def _parse_row_data_to_pydantic(
        cls,
        row: bs4.element.Tag,
        trading_day_beginning_datetime: datetime.datetime,
        row_id: int,
    ) -> DAMPointInTimePriceData:
        price_datetime, energy_prices = cls._parse_row(
            row,
            trading_day_beginning_datetime,
            row_id,
        )
        return DAMPointInTimePriceData(
            settlement_period_start_datetime=price_datetime,
            a1_price_in_rs_per_mwh=energy_prices[0],
            a2_price_in_rs_per_mwh=energy_prices[1],
            e1_price_in_rs_per_mwh=energy_prices[2],
            e2_price_in_rs_per_mwh=energy_prices[3],
            n1_price_in_rs_per_mwh=energy_prices[4],
            n2_price_in_rs_per_mwh=energy_prices[5],
            n3_price_in_rs_per_mwh=energy_prices[6],
            s1_price_in_rs_per_mwh=energy_prices[7],
            s2_price_in_rs_per_mwh=energy_prices[8],
            s3_price_in_rs_per_mwh=energy_prices[9],
            w1_price_in_rs_per_mwh=energy_prices[10],
            w2_price_in_rs_per_mwh=energy_prices[11],
            w3_price_in_rs_per_mwh=energy_prices[12],
            mcp_price_in_rs_per_mwh=energy_prices[13],
        )


class RTMHtmlParsingEngine(BaseHtmlParsingEngine):
    PRICE_TABLE_NUM_COLS = 19
    PRICE_COLUMN_OFFSET = 2
    DATA_ROW_OFFSET = 2

    @classmethod
    def _determine_column_offset_by_row_id(cls, row_id: int) -> int:
        """
        Determines the offset of the columns in the row based on the row id.
        Unfortunately, every row has a different number of columns, so we need
        to determine the offset based on the row id.
        """
        if row_id == 2:
            return 3
        if cls._is_hour_mark(row_id):
            return 2
        else:
            return (row_id - 1) % 2

    @classmethod
    def _parse_row_data_to_pydantic(
        cls,
        row: bs4.element.Tag,
        trading_day_beginning_datetime: datetime.datetime,
        row_id: int,
    ) -> RTMPointInTimePriceData:
        price_datetime, energy_prices = cls._parse_row(
            row,
            trading_day_beginning_datetime,
            row_id,
        )
        return RTMPointInTimePriceData(
            settlement_period_start_datetime=price_datetime,
            a1_price_in_rs_per_mwh=energy_prices[0],
            a2_price_in_rs_per_mwh=energy_prices[1],
            e1_price_in_rs_per_mwh=energy_prices[2],
            e2_price_in_rs_per_mwh=energy_prices[3],
            n1_price_in_rs_per_mwh=energy_prices[4],
            n2_price_in_rs_per_mwh=energy_prices[5],
            n3_price_in_rs_per_mwh=energy_prices[6],
            s1_price_in_rs_per_mwh=energy_prices[7],
            s2_price_in_rs_per_mwh=energy_prices[8],
            s3_price_in_rs_per_mwh=energy_prices[9],
            w1_price_in_rs_per_mwh=energy_prices[10],
            w2_price_in_rs_per_mwh=energy_prices[11],
            w3_price_in_rs_per_mwh=energy_prices[12],
            mcp_price_in_rs_per_mwh=energy_prices[13],
        )
