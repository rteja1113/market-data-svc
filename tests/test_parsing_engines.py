import pytest

from iex_app.api.models.data import DAMPointInTimePriceData, RTMPointInTimePriceData
from iex_app.scraping.parsing_engines import DAMHtmlParsingEngine, RTMHtmlParsingEngine


@pytest.fixture
def html_content(request):
    with open(request.param, "r") as f:
        return f.read()


@pytest.mark.parametrize(
    "parsing_engine, data_class, html_content",
    [
        (
            DAMHtmlParsingEngine(),
            DAMPointInTimePriceData,
            "./data/dam_prices_page.html",
        ),
        (
            RTMHtmlParsingEngine(),
            RTMPointInTimePriceData,
            "./data/rtm_prices_page.html",
        ),
    ],
    indirect=["html_content"],
)
def test_parse_doc_to_price_data(parsing_engine, data_class, html_content):
    price_data = parsing_engine.parse_doc_to_price_data(html_content)

    # assert that we have 96 settlement periods in the day
    assert len(price_data) == 96

    for spd in price_data:
        assert isinstance(spd, data_class)
        assert spd.settlement_period_start_datetime is not None
        assert spd.a1_price_in_rs_per_mwh is not None
