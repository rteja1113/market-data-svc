from __future__ import annotations

import datetime

from pydantic import BaseModel, model_validator


class TimeFrame(BaseModel):
    """
    A class that describes the Time Frame for the price.
    start_datetime should be less than end_datetime
    """

    start_datetime: datetime.datetime
    end_datetime: datetime.datetime

    @model_validator(mode="after")
    def validate_start_and_end_datetimes(self):
        if self.start_datetime > self.end_datetime:
            raise ValueError("start_datetime should be less than end_datetime")


if __name__ == "__main__":
    download_window = TimeFrame(
        start_datetime=datetime.datetime(2020, 1, 1),
        end_datetime=datetime.datetime(2019, 1, 1),
    )
    print(download_window)
