import datetime

from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from utils.utils import generate_open_meteo_config
from models.forecast import Forecast
from fastapi import APIRouter

from schemas.forecasts import ForecastDiffResponse
from utils.utils import ForecastRetrievalException

forecast_router = APIRouter(
    prefix="/forecasts",
    tags=["forecasts"]
)


@forecast_router.get("", name="Forecast vs measurement endpoint",
                     description="Retrieves the differences between the "
                                 "forecasted and measured weather data "
                                 "for the specified city.")
def get_forecasts_diff(city_name: str):
    forecast_pairs = Forecast.get_forecast_diffs(city_name=city_name)

    return [ForecastDiffResponse(city_name, **fp[0] - fp[1])
            for fp in forecast_pairs]


@forecast_router.post("", name="Fetch new forecast data endpoint",
                      description="Stores new weather forecast data for "
                                  "the specified city.")
def get_new_forecast(city_name: str,
                     start_date: datetime.date,
                     end_date: datetime.date):

    try:
        forecasts = Forecast.get_forecast(city_name,
                                          generate_open_meteo_config(
                                              {"city_name": city_name,
                                               "start_date": start_date,
                                               "end_date": end_date}))
    except ForecastRetrievalException as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": e.to_dict()}),
        )
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=jsonable_encoder({"total_new": len(forecasts)})
                        )
