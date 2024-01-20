from urllib.parse import urljoin

from iex_app.common.constants import BASE_MARKET_URL


class BasePricePageProperties:
    PAGE_URL = BASE_MARKET_URL
    NUM_COLS_IN_PRICE_TABLE = 1


class DAMPricePageProperties(BasePricePageProperties):
    PAGE_URL = urljoin(BASE_MARKET_URL, "areaprice.aspx")
    NUM_COLS_IN_PRICE_TABLE = 18


class RTMPricePageProperties(BasePricePageProperties):
    PAGE_URL = urljoin(BASE_MARKET_URL, "rtm_areaprice.aspx")
    NUM_COLS_IN_PRICE_TABLE = 19
