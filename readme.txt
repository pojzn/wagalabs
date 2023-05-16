
                        Wagalabs take home assignment

Assignment explanation

    The assignment was split into two parts:
        1. Create a CLI utility script which would fetch weather forecast data
            for user specified places and date ranges via a 3rd party API,
            and save the data to a CSV file/DB.
        2. Create a web server with an exposed endpoint for fetching
            the differences between forecasted and actually measured
            weather data.

Requirements

    Python 3.11.3 installed on your computer. Navigate to the "setup" folder
    and run the appropriate setup script.


Solution explanation

    The utility script is located in the root folder, under the name
    of "fetch_forecasts.py". It can be ran by passing it to the python
    interpreter. The CLI expects 3 arguments:
     1. City name (-c) - use double quotation marks if
                         the name contains whitespace
     2. Start date (-s) - date string in the ISO format (YYYY-MM-DD)
     3. End date (-e) - date string in the ISO format (YYYY-MM-DD)
    All of these are explained in the CLI, which can be seen by calling
    the script with the help (-h) argument.

    By default, it uses the open-meteo.com API to retrieve location
    coordinates and fetch specified data fields for the location
    (more info @ https://open-meteo.com/en/docs). The fetched data
    is saved to a SQLite database file, found in the root folder under
    the name of "waga.db".

    The web server is based on the FastAPI web framework.
    It is started by calling "uvicorn start_server:app" from the root folder.
    This will run and expose the server on the localhost (127.0.0.1)
    and port 8000 by default. To see the available endpoints, their methods
    and parameters, navigate to http://127.0.0.1/docs.

    In case of errors, please check the application error log file "error.log",
    located in the root folder.
