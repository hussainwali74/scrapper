#!/bin/bash

# Uses Uvicorn
# ENV='prod' uvicorn main:app --host 0.0.0.0

# Uses Gunicorn
GECKODRIVER_PATH="/root/geckodriver" ENV='prod' \
gunicorn main:app --bind 0.0.0.0:443 -w 3 -k uvicorn.workers.UvicornWorker \
--certfile=/etc/letsencrypt/live/www.roomie.pk/fullchain.pem \
--keyfile=/etc/letsencrypt/live/www.roomie.pk/privkey.pem \
--timeout 43_200 --daemon --access-logfile='app.log' --log-file='app.log'
