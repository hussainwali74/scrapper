from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, Base, get_db
from models.db_models.car import CarDB

from sqlalchemy.orm import Session
import crud
from os import getenv
from web_scrapper import get_car_info_from_web
from datetime import date
from api import api

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.api_router)

# car1 = Car(carName="toyota")
# @app.get('/url-list')
@app.get('/')
def get_all_urls():
    GECKODRIVER_PATH = getenv("GECKODRIVER_PATH")
    print("------- Bout to print gecko driver ")
    print(GECKODRIVER_PATH)
    url_list = [
        {'path': route.path, 'name': route.name}
        for route in app.routes
    ]
    return url_list


if __name__ == '__main__':
    pass
