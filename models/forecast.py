import datetime
from datetime import date
from dataclasses import dataclass

import requests
from sqlalchemy import Column, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, aliased
from sqlalchemy import select

from database.db import Base, DBSession
from utils.utils import ClientConfig, LoggingCtxManager


@dataclass
class Forecast(Base):
    """
    Forecast class used for ORM purposes.
    """

    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True)
    city_name: Mapped[str] = Column(String, nullable=False)
    request_date: Mapped[date] = Column(Date, nullable=False)
    measure_date: Mapped[date] = Column(Date, nullable=False, index=True)
    temp_min: Mapped[float] = Column(Float(precision=4), nullable=False)
    temp_max: Mapped[float] = Column(Float(precision=4), nullable=False)
    precipitation_sum: Mapped[float] = \
        Column(Float(precision=4), nullable=False)
    windspeed_max: Mapped[float] = Column(Float(precision=4), nullable=False)
    is_forecast: Mapped[bool] = mapped_column(init=False)

    def __post_init__(self):
        self.is_forecast = self.measure_date > self.request_date

    @staticmethod
    def get_forecast(city_name: str,
                     config: ClientConfig,
                     save_to_db: bool = True) -> list["Forecast"]:
        """
        Fetches data from the remote service based on the city name and
        passed configuration object, and by default saves it to the project
        specified database.

        Args:
            city_name (str): name of the city whose weather forecast will be fetched
            config (ClientConfig): configuration object which contains the url,
                                   parameters and response data handler function
            save_to_db (bool): flag which indicates if the data should be
                               saved to a database

        Returns:
            list[Forecast]
        """
        session = requests.Session()
        request = requests.Request(method="GET",
                                   url=config.api_url,
                                   params=config.params)

        with LoggingCtxManager():
            response = session.send(session.prepare_request(request))

        forecasts = config.handler_fn(city_name, response.json())

        if save_to_db:
            with LoggingCtxManager():
                with DBSession() as db_session:
                    db_session.add_all(forecasts)
                    db_session.commit()

        return forecasts

    @staticmethod
    def get_forecast_diffs(city_name: str):
        a = aliased(Forecast, name="a")
        b = aliased(Forecast, name="b")
        with DBSession() as db:
            forecasts = \
                db.execute(select(a, b).where(
                    a.city_name == city_name,
                    b.city_name == city_name,
                    a.measure_date == b.measure_date,
                    a.is_forecast != b.is_forecast)
                           .group_by(a.measure_date)
                           .order_by(a.measure_date)).fetchall()
            return forecasts

    def __sub__(self, other: "Forecast"):
        """
        Used for getting the differences between two Forecast objects.

        Args:
            other:

        Returns:

        """
        if self.measure_date != other.measure_date:
            raise ValueError("Cannot diff two Forecast "
                             "objects with different measurement dates.")
        measured = self if not self.is_forecast else other
        forecasted = self if self.is_forecast else other
        self.measure_date: datetime.date
        return {"measure_date": self.measure_date,
                "temp_min_diff":
                    forecasted.temp_min - measured.temp_min,
                "temp_max_diff":
                    forecasted.temp_max - measured.temp_max,
                "precipitation_diff":
                    forecasted.precipitation_sum -
                        measured.precipitation_sum,
                "windspeed_max_diff":
                    forecasted.windspeed_max - measured.windspeed_max}
