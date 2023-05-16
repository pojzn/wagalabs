import traceback
from dataclasses import dataclass
import logging
import requests


logging.basicConfig(filename="../error.log", filemode="a",
                    format="=============\n%(levelname)s | %(asctime)s \n"
                           "----------\n%(message)s=============\n",
                    datefmt="%m/%d/%Y %I:%M:%S %p",
                    level=logging.WARNING)


class LoggingCtxManager:
    """
    Context manager used to catch exceptions and log them to a log file.
    Will propagate exceptions further on.
    """

    def __init__(self, logger_name: str = "forecast",
                 level: int = logging.ERROR):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

    def __enter__(self):
        pass

    def __exit__(self, exc_type: Exception, exc_val: str, exc_tb: traceback):
        if exc_type is not None:
            self.logger.log(self.logger.level, msg=traceback.format_exc())


@dataclass
class ClientConfig:
    api_url: str
    params: dict
    handler_fn: callable


def get_city_lat_long(city_name: str) -> tuple[float, float]:
    """
    Utility function for retrieving lat/long coordinates of a specified city.
    Uses open-meteo.com API, which is free use for non-commercial cases
    at the time of writing.

    Args:
        city_name (str): name of the city whose coordinates will be fetched.

    Returns:
        tuple of floats (city coordinates)
    """
    with LoggingCtxManager():
        response = requests.get(f"https://geocoding-api.open-meteo.com/v1/"
                                f"search?name={city_name}&count=1&language=en"
                                f"&format=json").json()

    response = response.get("results")
    if response is None:
        raise ForecastRetrievalException(
            ForecastRetrievalException.INVALID_CITY)
    # Index accessed since the API returns a list - specified length is 1
    return response[0]["latitude"], response[0]["longitude"]


@dataclass
class ForecastRetrievalException(Exception):
    INVALID_DATE = "Invalid date"
    INVALID_CITY = "Invalid city"
    message: str

    def to_dict(self):
        if self.message == ForecastRetrievalException.INVALID_DATE:
            return [{"loc":
                         ["query", "start_date"],
                     "type": "value_error.date",
                     "msg": self.message.lower()},
                    {"loc": ["query", "end_date"],
                     "type": "value_error.date",
                     "msg": self.message.lower()}]
        elif self.message == ForecastRetrievalException.INVALID_CITY:
            return [{"loc": ["query", "city_name"],
                     "type": "value_error.str",
                     "msg": self.message.lower()}]

        return [{"loc":
                     ["unknown", "unknown"],
                 "type": "value_error.unknown",
                 "msg": self.message.lower()},
                ]


def generate_open_meteo_config(args: dict) -> ClientConfig:
    """
    Generates and returns a valid ClientConfig object, which contains
    the base url and all query parameters needed to make a
    successful HTTP request, and a reference to the handler function
    which will parse the incoming data and transform it into Forecast objects.

    Args:
        args (dict): dictionary containing the city_name,
                     start_date and end_date parameters

    Returns:
        ClientConfig
    """
    from utils.handlers import handle_open_meteo_data

    latitude, longitude = get_city_lat_long(args["city_name"])
    params = {"latitude": latitude,
              "longitude": longitude,
              "start_date": args["start_date"],
              "end_date": args["end_date"],
              "timezone": "auto",
              "temperature_unit": "celsius",
              "windspeed_unit": "kmh",
              "precipitation_unit": "mm",
              "daily": "temperature_2m_min,temperature_2m_max,"
                       "precipitation_sum,windspeed_10m_max"
              }
    return ClientConfig(api_url="https://api.open-meteo.com/v1/forecast?",
                        params=params,
                        handler_fn=handle_open_meteo_data)