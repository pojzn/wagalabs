from argparse import Namespace

from database.db import configure_database
from models.forecast import Forecast
from utils.utils import generate_open_meteo_config
import argparse
from datetime import date

if __name__ == "__main__":
    # Sets up the database if it is not initialized
    configure_database()

    parser = argparse.ArgumentParser(description="Fetches and stores new "
                                                 "weather forecast data "
                                                 "for the specified town or "
                                                 "city and within the "
                                                 "specified start and end "
                                                 "dates.")
    parser.add_argument("-c",
                        "--city_name",
                        type=str,
                        help="City or town name whose weather forecast is "
                             "being retrieved. Please use double quotation "
                             "marks if the name contains multiple words.",
                        required=True)

    parser.add_argument("-s",
                        "--start_date",
                        type=date.fromisoformat,
                        help="Starting date used for forecast retrieval.",
                        required=True)

    parser.add_argument("-e",
                        "--end_date",
                        type=date.fromisoformat,
                        help="Ending date used for forecast retrieval.",
                        required=True)
    # Contains .city_name, .start_date, .end_date attrs
    args: Namespace = parser.parse_args()

    client_config = generate_open_meteo_config(vars(args))

    forecasts = Forecast.get_forecast(args.city_name, config=client_config)
    print(f"Succesfully fetched {len(forecasts)} forecasts between "
          f"{args.start_date} and {args.end_date} for the city "
          f"of {args.city_name}.")
