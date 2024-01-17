from __future__ import annotations

import abc
import datetime
import logging
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from iex_app.api.models.data import BasePointInTimePriceData
from iex_app.common.constants import BASE_MARKET_URL
from iex_app.common.models import DownloadWindow
from iex_app.scraping.parsing_engines import BaseHtmlParsingEngine

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)


class BaseDataDownloaderBot(abc.ABC):
    """
    A base class for the data_archived downloader bot
    """

    DEFAULT_BATCH_SIZE_IN_DAYS = 1

    def __init__(
        self,
        web_driver: RemoteWebDriver,
        parsing_engine: BaseHtmlParsingEngine,
        price_table_num_columns: int,
    ):
        self.driver: RemoteWebDriver = web_driver
        self.parsing_engine: BaseHtmlParsingEngine = parsing_engine
        self.price_table_num_columns = price_table_num_columns

    def extract_delivery_period_dropdown_from_driver(self) -> WebElement:
        """
        Extracts the delivery period dropdown from the driver.
        The dropdown is the one with the text "Delivery Period"
        """
        possible_dropdowns = self.driver.find_elements(
            By.CLASS_NAME,
            "mkt_filter_lbl",
        )
        for possible_dropdown in possible_dropdowns:
            span_element = possible_dropdown.find_element(By.TAG_NAME, "span")
            if span_element.text == "Delivery Period":
                return possible_dropdown

        raise ValueError("Could not find delivery period dropdown")

    def render_page_with_new_dates(
        self, start_datetime: datetime.datetime, end_datetime: datetime.datetime
    ):
        self.set_start_date_to_page(start_datetime)
        self.set_end_date_to_page(end_datetime)
        self.click_update_report_button()

    def set_start_date_to_page(self, start_datetime: datetime.datetime):
        """
        Sets the start date to the page, using the given datetime.
        Executes javascript code to set start date to do this.
        """
        self._set_date_to_page(
            start_datetime,
            "ctl00_InnerContent_calFromDate_txt_Date",
        )

    def set_end_date_to_page(self, end_datetime: datetime.datetime):
        """
        Sets the end date to the page, using the given datetime.
        Executes javascript code to set end date to do this.
        """
        self._set_date_to_page(
            end_datetime,
            "ctl00_InnerContent_calToDate_txt_Date",
        )

    def _set_date_to_page(
        self, datetime_to_set: datetime.datetime, date_input_element_id: str
    ):
        date_input_element = self.get_input_element_from_driver(
            date_input_element_id,
        )
        date_input_element.click()

        # use provided datetime to set the date
        formatted_date = "'" + datetime_to_set.strftime("%d/%m/%Y") + "'"
        js_code_to_execute = (
            f"document.getElementById('{date_input_element_id}')."
            f"value={formatted_date};"
        )
        script_executor = self.driver.execute_script
        script_executor(js_code_to_execute)

    def get_input_element_from_driver(self, input_element_id: str) -> WebElement:
        return self.driver.find_element(By.ID, input_element_id)

    def click_update_report_button(self):
        """
        Clicks the update report button to render the page
        with new data for new dates
        """
        update_report_button = self.get_input_element_from_driver(
            "ctl00_InnerContent_btnUpdateReport",
        )
        update_report_button.click()

    @staticmethod
    def select_and_click_range_from_delivery_period_dropdown(
        delivery_period_dropdown: WebElement,
    ) -> None:
        """
        Selects the "Select Range" option from the delivery
        period dropdown and clicks it
        """
        dropdown_options = delivery_period_dropdown.find_elements(
            By.TAG_NAME,
            "option",
        )
        for dropdown_option in dropdown_options:
            if dropdown_option.text == "-Select Range-":
                dropdown_option.click()
                return
        raise ValueError("Could not find option to Select Range option")

    def table_present_in_page(self, driver: RemoteWebDriver) -> bool:
        """
        Checks if the table is present in the page.
        The table is the one with price_table_num_columns columns
        """
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            try:
                num_cols = int(table.get_attribute("cols"))
            except Exception:
                num_cols = 0
            if num_cols == self.price_table_num_columns:
                return True
        return False

    def _wait_for_table_to_load(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(self.table_present_in_page)

    def download_data_for_window(
        self, download_window: DownloadWindow
    ) -> list[BasePointInTimePriceData]:
        """
        Downloads the data_archived for the date range. The data
        is downloaded in batches of batch_size_in_days
        The steps it follows are:
        1. Extract the delivery period dropdown from the driver
        2. Select the "Select Range" option from the dropdown
        3. Render the page with the new dates
        4. Download the data_archived for the new dates
        """
        price_data = []
        try:
            delivery_period_dropdown = (
                self.extract_delivery_period_dropdown_from_driver()
            )
            self.select_and_click_range_from_delivery_period_dropdown(
                delivery_period_dropdown,
            )

            while download_window.start_datetime <= download_window.end_datetime:
                self.render_page_with_new_dates(
                    download_window.start_datetime,
                    download_window.start_datetime
                    + datetime.timedelta(
                        days=self.DEFAULT_BATCH_SIZE_IN_DAYS - 1,
                    ),
                )
                try:
                    self._wait_for_table_to_load()
                except TimeoutError:
                    logger.error(
                        "Timeout error occurred while waiting for the "
                        "data to load. Closing driver",
                    )
                    continue

                downloaded_dam_data = self.parsing_engine.parse_doc_to_price_data(
                    self.driver.page_source,
                )
                price_data.extend(downloaded_dam_data)
                logger.debug(
                    f"Downloaded data_archived for datetime:"
                    f" {download_window.start_datetime}",
                )
                download_window.start_datetime += datetime.timedelta(
                    days=self.DEFAULT_BATCH_SIZE_IN_DAYS,
                )
        except Exception as e:
            logging.exception(
                f"Error occurred while downloading data_archived for datetime"
                f" {download_window.start_datetime}. Closing driver ",
                exc_info=e,
            )
        finally:
            self.driver.close()
        return price_data


class DAMPriceDataDownloaderBot(BaseDataDownloaderBot):
    DAM_MARKET_PRICE_URL = os.path.join(BASE_MARKET_URL, "areaprice.aspx")
    DAM_TABLE_NUM_COLS = 18

    def __init__(
        self,
        web_driver: RemoteWebDriver,
        parsing_engine: BaseHtmlParsingEngine,
    ):
        super().__init__(web_driver, parsing_engine, self.DAM_TABLE_NUM_COLS)
        # post init
        self.driver.get(self.DAM_MARKET_PRICE_URL)


class RTMPriceDataDownloaderBot(BaseDataDownloaderBot):
    RTM_MARKET_PRICE_URL = os.path.join(BASE_MARKET_URL, "rtm_areaprice.aspx")
    RTM_TABLE_NUM_COLS = 19

    def __init__(
        self,
        web_driver: RemoteWebDriver,
        parsing_engine: BaseHtmlParsingEngine,
    ):
        super().__init__(web_driver, parsing_engine, self.RTM_TABLE_NUM_COLS)
        # post init
        self.driver.get(self.RTM_MARKET_PRICE_URL)
