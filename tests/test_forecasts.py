import datetime

import pytest
import numpy as np

from utils.utils import ForecastRetrievalException, get_city_lat_long


@pytest.fixture(scope="module")
def openmeteo_data():
    import datetime
    num_of_forecast_days = 10
    forecast_data = [np.random.uniform(0, 100, size=4).astype(str)
                     for _ in range(num_of_forecast_days)]
    data = {"time": [],
            "temperature_2m_min": [],
            "temperature_2m_max": [],
            "precipitation_sum": [],
            "windspeed_10m_max": []}
    for i, forecast in enumerate(forecast_data):
        data["time"].append(str(datetime.date.today() +
                                datetime.timedelta(days=i)
                                )
                            )
        data["temperature_2m_min"].append(forecast[0])
        data["temperature_2m_max"].append(forecast[1])
        data["precipitation_sum"].append(forecast[2])
        data["windspeed_10m_max"].append(forecast[3])

    return {"daily": data}


def bad_openmeteo_data():
    # Each element contains data of the wrong data type at an increasing index
    error_data = [
        ["abc", "17.591", "39.2", "12", "10"],
        ["2023-05-01", object(), "42.1", "5.39", "5.15"],
        ["2023-05-02", "7", "Lorem Ipsum", "20.3", "3.71"],
        ["2023-05-03", "24.2", "32.55", __name__, "0"],
        ["2023-05-04", "12.14", "37.14", "14.6", np]
    ]

    for data in error_data:
        yield {"daily":
                   {"time": [data[0]],
                    "temperature_2m_min": [data[1]],
                    "temperature_2m_max": [data[2]],
                    "precipitation_sum": [data[3]],
                    "windspeed_10m_max": [data[4]]
                    }
               }


def test_handle_open_meteo_data(openmeteo_data):
    from utils.handlers import handle_open_meteo_data

    city_name = "Novi Sad"
    forecasts = handle_open_meteo_data(city_name, openmeteo_data)

    meteo_data = openmeteo_data["daily"]
    assert len(meteo_data["time"]) == len(forecasts)

    for i, forecast in enumerate(forecasts):
        assert forecast.id is None
        assert datetime.date.today() == forecast.request_date
        assert datetime.date.today() + datetime.timedelta(days=i) \
               == forecast.measure_date
        assert city_name == forecast.city_name
        assert datetime.date.fromisoformat(meteo_data["time"][i]) == \
               forecast.measure_date
        assert float(meteo_data["temperature_2m_min"][i]) == forecast.temp_min
        assert float(meteo_data["temperature_2m_max"][i]) == forecast.temp_max
        assert float(meteo_data["precipitation_sum"][i]) == \
               forecast.precipitation_sum
        assert float(meteo_data["windspeed_10m_max"][i]) == \
               forecast.windspeed_max

    with pytest.raises(ForecastRetrievalException):
        error_response = {"error": True,
                          "reason": "Some error reason."}
        handle_open_meteo_data(city_name, error_response)

    for data in bad_openmeteo_data():
        with pytest.raises((ValueError, TypeError, ForecastRetrievalException)):
            handle_open_meteo_data(city_name, data)


def test_get_city_lat_long():
    lat, long = get_city_lat_long(city_name="Novi Sad")
    assert isinstance(lat, float)
    assert isinstance(long, float)

    with pytest.raises(ForecastRetrievalException):
        get_city_lat_long(city_name="")
