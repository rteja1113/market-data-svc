import datetime
from unittest import mock

import pytest

from src.common.models import TimeFrame
from src.marketdata.schemas import DAMPointInTimePriceData, RTMPointInTimePriceData
from src.migrations.automated.scraping.parsing_engines import (
    DAMHtmlParsingEngine,
    RTMHtmlParsingEngine,
)
from src.migrations.automated.scraping.price_data_bot import PriceDataDownloaderBot
from src.migrations.automated.scraping.price_page_properties import (
    DAMPricePageProperties,
    RTMPricePageProperties,
)


@pytest.fixture
def download_window():
    return TimeFrame(
        start_datetime=datetime.datetime(2020, 1, 1),
        end_datetime=datetime.datetime(2021, 1, 2),
    )


@pytest.fixture
def mock_web_driver():
    return mock.Mock()


@pytest.mark.parametrize(
    "parsing_engine, page_properties, data_class",
    [
        (DAMHtmlParsingEngine(), DAMPricePageProperties(), DAMPointInTimePriceData),
        (RTMHtmlParsingEngine(), RTMPricePageProperties(), RTMPointInTimePriceData),
    ],
)
def test_web_bot_initialization(
    parsing_engine, page_properties, data_class, mock_web_driver, download_window
):
    _ = PriceDataDownloaderBot(
        web_driver=mock_web_driver,
        parsing_engine=parsing_engine,
        page_properties=page_properties,
    )
    mock_web_driver.get.assert_called_once_with(page_properties.PAGE_URL)


def test_download_data_for_window():
    pass
