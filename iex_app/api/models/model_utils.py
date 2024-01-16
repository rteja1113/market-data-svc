import pandas as pd
from iex_app.api.models.data import BasePointInTimePriceData


def convert_list_of_price_data_to_dataframe(price_data: list[BasePointInTimePriceData]) -> pd.DataFrame:
    """
    Converts the list of price data_archived to a dataframe
    """
    price_data_dict = {}
    for price_data_obj in price_data:
        _ = price_data_obj.model_dump()
        price_data_dict[price_data_obj.settlement_period_start_datetime] = price_data_obj.model_dump(exclude=set(["settlement_period_start_datetime"]))

    price_data_df = pd.DataFrame.from_dict(price_data_dict, orient="index")
    price_data_df.sort_index(inplace=True)
    return price_data_df
