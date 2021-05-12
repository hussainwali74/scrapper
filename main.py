from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from os import getenv
from sys import stdout
from api import api

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://192.46.223.236"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.api_router)

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

# file_handler = RotatingFileHandler("app.log", maxBytes=1.049e+7, backupCount=3)  # maxBytes 10 MB
# file_handler.setFormatter(log_format)
# rootLogger.addHandler(file_handler)

stream_handler = StreamHandler(stdout )
stream_handler.setFormatter(log_format)
rootLogger.addHandler(stream_handler)

gunicorn_logger = logging.getLogger('gunicorn.error')
rootLogger.addHandler(*gunicorn_logger.handlers)

# car1 = Car(carName="toyota")
# @app.get('/url-list')
@app.get('/')
def get_all_urls():
    GECKODRIVER_PATH = getenv("GECKODRIVER_PATH")
    logging.info("------- Bout to print gecko driver ")
    logging.info(GECKODRIVER_PATH)
    url_list = [
        {'path': route.path, 'name': route.name}
        for route in app.routes
    ]
    return url_list


if __name__ == '__main__':
    pass
