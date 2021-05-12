#!/bin/bash

# Uses Uvicorn
# ENV='prod' uvicorn main:app --host 0.0.0.0

# Uses Gunicorn
GECKODRIVER_PATH="/root/geckodriver" ENV='prod' gunicorn main:app --bind 0.0.0.0:8000 -w 3 -k uvicorn.workers.UvicornWorker \
--timeout 28_800 & disown;
