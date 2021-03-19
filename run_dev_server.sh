#!/bin/bash

# For development
uvicorn main:app --host 0.0.0.0 --reload

# For full production
# gunicorn -k uvicorn.workers.UvicornWorker
