import datetime

from selenium import webdriver

from src.common.models import TimeFrame
from src.marketdata.schema_utils import convert_list_of_price_data_to_dataframe
from src.migrations.automated.scraping.parsing_engines import DAMHtmlParsingEngine
from src.migrations.automated.scraping.price_data_bot import PriceDataDownloaderBot
from src.migrations.automated.scraping.price_page_properties import (
    DAMPricePageProperties,
)

# We initialize the bot with a Chrome webdriver for downloading DAM price data
dam_price_web_bot = PriceDataDownloaderBot(
    web_driver=webdriver.Chrome(),
    parsing_engine=DAMHtmlParsingEngine(),
    page_properties=DAMPricePageProperties(),
)
# initialize the download window for the bot
download_window = TimeFrame(
    start_datetime=datetime.datetime(2021, 1, 1),
    end_datetime=datetime.datetime(2021, 1, 3),
)

# download the data for the window
dam_price_data = dam_price_web_bot.download_data_for_window(download_window)

# convert the dam_price_data to a dataframe
dam_price_data_df = convert_list_of_price_data_to_dataframe(dam_price_data)
print(dam_price_data_df.head())
print(dam_price_data_df.tail())
