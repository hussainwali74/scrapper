#!/bin/bash

# For development
#uvicorn main:app --host 0.0.0.0 --reload

# For production
gunicorn main:app --bind 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker
