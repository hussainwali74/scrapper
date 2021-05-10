#!/bin/bash

# For development
#uvicorn main:app --host 0.0.0.0 --reload

# For production
GECKODRIVER_PATH="/home/teemo/softwares/geckodriver" \
ENV="prod" gunicorn main:app --preload --bind 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker --timeout 21_600
#gunicorn main:app --bind 0.0.0.0:8000 -w 1