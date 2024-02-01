from __future__ import annotations

import datetime
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from iex_app.api.models.data import BasePointInTimePriceData
from iex_app.common.models import DownloadWindow
from iex_app.scraping.parsing_engines import BaseHtmlParsingEngine
from iex_app.scraping.price_page_properties import BasePricePageProperties

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


class PriceDataDownloaderBot:
    """
    A Bot for downloading price data from the IEX website.
    """

    DEFAULT_BATCH_SIZE_IN_DAYS = 1

    def __init__(
        self,
        web_driver: RemoteWebDriver,
        parsing_engine: BaseHtmlParsingEngine,
        page_properties: BasePricePageProperties,
    ):
        self._driver: RemoteWebDriver = web_driver
        self._parsing_engine: BaseHtmlParsingEngine = parsing_engine
        self._price_table_num_columns = page_properties.NUM_COLS_IN_PRICE_TABLE
        self._driver.get(page_properties.PAGE_URL)

    def _extract_delivery_period_dropdown_from_driver(self) -> WebElement:
        """
        Extracts the delivery period dropdown from the _driver.
        The dropdown is the one with the text "Delivery Period"
        """
        possible_dropdowns = self._driver.find_elements(
            By.CLASS_NAME,
            "mkt_filter_lbl",
        )
        for possible_dropdown in possible_dropdowns:
            span_element = possible_dropdown.find_element(By.TAG_NAME, "span")
            if span_element.text == "Delivery Period":
                return possible_dropdown

        raise ValueError("Could not find delivery period dropdown")

    def _render_page_with_new_dates(
        self, start_datetime: datetime.datetime, end_datetime: datetime.datetime
    ):
        self._set_start_date_to_page(start_datetime)
        self._set_end_date_to_page(end_datetime)
        self._click_update_report_button()

    def _set_start_date_to_page(self, start_datetime: datetime.datetime):
        """
        Sets the start date to the page, using the given datetime.
        Executes javascript code to set start date to do this.
        """
        self._set_date_to_page(
            start_datetime,
            "ctl00_InnerContent_calFromDate_txt_Date",
        )

    def _set_end_date_to_page(self, end_datetime: datetime.datetime):
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
        date_input_element = self._get_input_element_from_driver(
            date_input_element_id,
        )
        date_input_element.click()

        # use provided datetime to set the date
        formatted_date = "'" + datetime_to_set.strftime("%d/%m/%Y") + "'"
        js_code_to_execute = (
            f"document.getElementById('{date_input_element_id}')."
            f"value={formatted_date};"
        )
        script_executor = self._driver.execute_script
        script_executor(js_code_to_execute)

    def _get_input_element_from_driver(self, input_element_id: str) -> WebElement:
        return self._driver.find_element(By.ID, input_element_id)

    def _click_update_report_button(self):
        """
        Clicks the update report button to render the page
        with new data for new dates
        """
        update_report_button = self._get_input_element_from_driver(
            "ctl00_InnerContent_btnUpdateReport",
        )
        update_report_button.click()

    @staticmethod
    def _select_and_click_range_from_delivery_period_dropdown(
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

    def _table_present_in_page(self, driver: RemoteWebDriver) -> bool:
        """
        Checks if the table is present in the page.
        The table is the one with _price_table_num_columns columns
        """
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            try:
                num_cols = int(table.get_attribute("cols"))
            except Exception:
                num_cols = 0
            if num_cols == self._price_table_num_columns:
                return True
        return False

    def _wait_for_table_to_load(self):
        wait = WebDriverWait(self._driver, 20)
        wait.until(self._table_present_in_page)

    def download_data_for_window(
        self, download_window: DownloadWindow
    ) -> list[BasePointInTimePriceData]:
        """
        Downloads the data_archived for the date range. The data
        is downloaded in batches of batch_size_in_days
        The steps it follows are:
        1. Extract the delivery period dropdown from the _driver
        2. Select the "Select Range" option from the dropdown
        3. Render the page with the new dates
        4. Download the data_archived for the new dates
        """
        price_data = []
        try:
            delivery_period_dropdown = (
                self._extract_delivery_period_dropdown_from_driver()
            )
            self._select_and_click_range_from_delivery_period_dropdown(
                delivery_period_dropdown,
            )

            while download_window.start_datetime <= download_window.end_datetime:
                self._render_page_with_new_dates(
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
                        "data to load. Closing _driver",
                    )
                    continue

                downloaded_price_data = self._parsing_engine.parse_doc_to_price_data(
                    self._driver.page_source,
                )
                price_data.extend(downloaded_price_data)
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
                f" {download_window.start_datetime}. Closing _driver ",
                exc_info=e,
            )
        finally:
            self._driver.close()
        return price_data
