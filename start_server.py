from fastapi import FastAPI

from database.db import configure_database
from routers.forecasts import forecast_router

app = FastAPI(title="WagaLabs Assignment")

app.include_router(forecast_router, prefix="/api/v1")


@app.on_event("startup")
def server_startup():
    configure_database()
