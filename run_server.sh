#!/bin/bash

# Uses Uvicorn
# ENV='prod' uvicorn main:app --host 0.0.0.0

# Uses Gunicorn
ENV='prod' gunicorn main:app --bind 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker --timeout 28_800
