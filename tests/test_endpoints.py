import datetime
import requests
import pytest
from fastapi.testclient import TestClient
from starlette import status

from start_server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_forecast_diffs(client):

    base_url = "/api/v1/forecasts"
    response = client.get(url=base_url)

    assert response.status_code != requests.codes["OK"]

    city_name = "Novi Sad"
    params = {"city_name": city_name}
    response = client.get(url=base_url,
                          params=params)

    assert response.status_code == requests.codes["OK"]
    response_json = response.json()

    for diff in response_json:
        assert list(diff.keys()) == ["city_name","measure_date",
                                     "temp_min_diff", "temp_max_diff",
                                     "precipitation_diff", "windspeed_max_diff"]
        assert diff["city_name"] == city_name
        assert isinstance(diff["measure_date"], str) \
               and datetime.date.fromisoformat(diff["measure_date"])
        assert isinstance(diff["temp_min_diff"], float)
        assert isinstance(diff["temp_max_diff"], float)
        assert isinstance(diff["precipitation_diff"], float)
        assert isinstance(diff["windspeed_max_diff"], float)

    city_name = "Some place that definitely doesn't exist on planet Earth"
    params = {"city_name": city_name}
    response = client.get(url=base_url,
                          params=params)

    assert response.status_code == requests.codes["OK"]
    response_json = response.json()
    assert len(response_json) == 0


@pytest.mark.parametrize("params, expected_errs", [
    ({"city_name": None,
      "start_date": "2023-05-01",
      "end_date": "2023-05-10"},
     [{"msg": "invalid city",
      "type": "value_error.str",
      "field": "city_name"}]),
    ({"city_name": "Novi Sad",
      "start_date": None,
      "end_date": "2023-05-10"},
     [{"msg": "invalid date format",
      "type": "value_error.date",
      "field": "start_date"}]),
    ({"city_name": "Novi Sad",
      "start_date": "2023-05-01",
      "end_date": None},
     [{"msg": "invalid date format",
      "type": "value_error.date",
      "field": "end_date"}]),
    ({"city_name": "Novi Sad",
      "start_date": "2523-05-01",
      "end_date": "2023-05-10"},
     [{"msg": "invalid date",
       "type": "value_error.date",
       "field": "start_date"},
      {"msg": "invalid date",
       "type": "value_error.date",
       "field": "end_date"}]),
    ({"city_name": "Novi Sad",
      "start_date": "2523-05-01",
      "end_date": "2823-05-10"},
     [{"msg": "invalid date",
       "type": "value_error.date",
       "field": "start_date"},
      {"msg": "invalid date",
       "type": "value_error.date",
       "field": "end_date"}]),
    ({"city_name": "Novi Sad",
      "start_date": "aaa",
      "end_date": "bbb"},
     [{"msg": "invalid date format",
       "type": "value_error.date",
       "field": "start_date"},
      {"msg": "invalid date format",
       "type": "value_error.date",
       "field": "end_date"}])
])
def test_fail_fetch_new_forecasts(client, params, expected_errs):
    base_url = "/api/v1/forecasts"

    response = client.post(url=base_url,
                           params=params)

    assert response.status_code != requests.codes["OK"]
    response_json = response.json()

    assert len(response_json["detail"]) >= 1
    for expected_err, reason in zip(expected_errs, response_json["detail"]):
        assert reason["loc"][0] == "query"
        assert reason["loc"][1] == expected_err["field"]
        assert reason["msg"] == expected_err["msg"]
        assert reason["type"] == expected_err["type"]


@pytest.mark.parametrize("params",
                         [{"city_name": "Novi Sad",
                           "start_date": datetime.date.today(),
                           "end_date": datetime.date.today() +
                                       datetime.timedelta(days=4)}
                          ])
def test_fetch_new_forecasts(client, params):
    base_url = "/api/v1/forecasts"
    response = client.post(url=base_url,
                           params=params)

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["total_new"] == 5
