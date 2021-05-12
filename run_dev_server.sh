#!/bin/bash

# For development (Firefox browser opens)
#uvicorn main:app --host 0.0.0.0 --reload

# For production (Firefox runs in headless mode)
GECKODRIVER_PATH="/home/teemo/softwares/geckodriver" \
ENV="prod" gunicorn main:app --preload --bind 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker --timeout 21_600
#gunicorn main:app --bind 0.0.0.0:8000 -w 1
