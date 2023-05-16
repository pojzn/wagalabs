import datetime
from datetime import date

from utils.utils import ForecastRetrievalException, LoggingCtxManager


def handle_open_meteo_data(city_name: str,
                           response_data: dict) -> list["Forecast"]:
    from models.forecast import Forecast
    """
    Handler function for open-meteo.com data.
    Converts the received data into Forecast objects.

    Args:
        city_name (str): name of the city whose forecast data has been received
        response_data (dict): dict containing JSON response data

    Returns:
        list[Forecast]
    """
    if response_data.get("error"):
        raise ForecastRetrievalException(response_data["reason"])

    sanitizers = {"time": lambda ts: date.fromisoformat(ts),
                  "temperature_2m_min":
                      lambda temp: float(temp) if temp is not None else 0.0,
                  "temperature_2m_max":
                      lambda temp: float(temp) if temp is not None else 0.0,
                  "precipitation_sum":
                      lambda p_sum: float(p_sum) if p_sum is not None else 0.0,
                  "windspeed_10m_max":
                      lambda wind: float(wind) if wind is not None else 0.0}

    with LoggingCtxManager():
        sanitized_data = [list(map(sanitizers[key], values))
                          for key, values in response_data["daily"].items()]

    today = datetime.date.today()

    forecasts = [Forecast(city_name, today, *data)
                 for data in zip(*sanitized_data)]

    return forecasts