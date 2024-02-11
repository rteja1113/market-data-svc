import datetime

import pandas as pd
import pytest

from iex_app.api.models.model_utils import convert_list_of_price_data_to_dataframe
from iex_app.api.models.pydantic_models import (
    DAMPointInTimePriceData,
    RTMPointInTimePriceData,
)
from iex_app.common.constants import MARKET_TZ


@pytest.fixture
def mock_datetime():
    return MARKET_TZ.localize(datetime.datetime(2022, 1, 1))


@pytest.fixture
def dam_price_data(mock_datetime):
    return [
        DAMPointInTimePriceData(
            settlement_period_start_datetime=mock_datetime,
            a1_price_in_rs_per_mwh=10.0,
            a2_price_in_rs_per_mwh=10.0,
            e1_price_in_rs_per_mwh=10.0,
            e2_price_in_rs_per_mwh=10.0,
            n1_price_in_rs_per_mwh=10.0,
            n2_price_in_rs_per_mwh=10.0,
            n3_price_in_rs_per_mwh=10.0,
            s1_price_in_rs_per_mwh=10.0,
            s2_price_in_rs_per_mwh=10.0,
            s3_price_in_rs_per_mwh=10.0,
            w1_price_in_rs_per_mwh=10.0,
            w2_price_in_rs_per_mwh=10.0,
            w3_price_in_rs_per_mwh=10.0,
            mcp_price_in_rs_per_mwh=10.0,
        )
    ]


@pytest.fixture
def rtm_price_data(mock_datetime):
    return [
        RTMPointInTimePriceData(
            settlement_period_start_datetime=mock_datetime,
            a1_price_in_rs_per_mwh=10.0,
            a2_price_in_rs_per_mwh=10.0,
            e1_price_in_rs_per_mwh=10.0,
            e2_price_in_rs_per_mwh=10.0,
            n1_price_in_rs_per_mwh=10.0,
            n2_price_in_rs_per_mwh=10.0,
            n3_price_in_rs_per_mwh=10.0,
            s1_price_in_rs_per_mwh=10.0,
            s2_price_in_rs_per_mwh=10.0,
            s3_price_in_rs_per_mwh=10.0,
            w1_price_in_rs_per_mwh=10.0,
            w2_price_in_rs_per_mwh=10.0,
            w3_price_in_rs_per_mwh=10.0,
            mcp_price_in_rs_per_mwh=10.0,
        )
    ]


@pytest.fixture
def price_data(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "price_data", ["dam_price_data", "rtm_price_data"], indirect=True
)
def test_convert_list_of_price_data_to_dataframe(price_data):
    df = convert_list_of_price_data_to_dataframe(price_data)
    # Add your assertions here
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.shape[0] == 1
