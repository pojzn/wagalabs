import datetime
from pydantic.dataclasses import dataclass


@dataclass
class ForecastDiffResponse:
    city_name: str
    measure_date: datetime.date
    temp_min_diff: float
    temp_max_diff: float
    precipitation_diff: float
    windspeed_max_diff: float
