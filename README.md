
### Requirements 
Python==3.8

### Information about FastAPI query parameters

Using the search car API from route `/car/search` uses 
following conventions to add meaning to query parameters.
E.g. data_gt means date grater then or equal to specified date.

    INTEGER1 eq INTEGER2
         INTEGER1 is equal to INTEGER2

    INTEGER1 ge INTEGER2
         INTEGER1 is greater than or equal to INTEGER2

    INTEGER1 gt INTEGER2
         INTEGER1 is greater than INTEGER2

    INTEGER1 le INTEGER2
         INTEGER1 is less than or equal to INTEGER2

    INTEGER1 lt INTEGER2
        INTEGER1 is less than INTEGER2

    INTEGER1 ne INTEGER2
        INTEGER1 is not equal to INTEGER2

#### Instructions to Run

Install python packages

    pip install -r requirements

##### Note

If error installing psycopg2 use the link below.
https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python

Install Gecko-driver driver

    https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu

App runs on port `8000`
Need to specify database credentials in `database.py`
Set environment variables `FIREFOX_BIN` Path to firefox executable,
`GECKODRIVER_PATH` path to geckodriver executable.

### Project Deployment Information
This project is currently deployed on `linode`. Project name is `car-scrapo`.
Directory `/root/scrapper/`.

##### Starting Web Server
    
    ./run_server.sh

##### Instructions on crontab
You need curl for this.
In crontab paste the following command to run code at 00:30 every
night. To access cronjobs for current user: `crontab -e`.

    30 0 * * * /<path_to_project_directory>/run_add_cars.sh

Here first number is minutes, second is hours.

Where <path_to_project_directory> is your local path to project.

##### Resources:
https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f

##### Others

Old procfile contents

    web: ENV="prod" uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}

    web: ENV="prod" gunicorn main:app --preload -k uvicorn.workers.UvicornWorker --timeout 21_000 --max-requests 5
    --bind="0.0.0.0:8000"

#### Sample queries
https://localhost/car/search?price_ge=26_000&mileage_le=5_000&limit=100

### Database
Database being used is PostgreSQL. It is also on the same server as the app.

#### Check Cars in DB
To access DB: `sudo -u postgres psql scrapper_db`

    scrapper_db=# SELECT id, car_name FROM cars ORDER BY id DESC;

#### Logrotate 
location: `/etc/logrotate.d/scrapper.conf`
```bash
    /root/scrapper/app.log {
    daily
    rotate 3
    size 10M
    dateext
    }
```

#### Adding Certificates to Gunicorn to enable HTTPS
https://stackoverflow.com/questions/51340872/can-i-certify-website-without-domain-name#:~:text=LetsEncrypt%20does%20not%20issue%20certs,use%20to%20access%20the%20site.
https://stackoverflow.com/questions/7406805/running-gunicorn-on-https

self sign the certificates

    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

Make Gunicorn use SSL

    gunicorn --certfile=server.crt --keyfile=server.key --bind 0.0.0.0:443 test:app


## Depricated Heroku Section

### Heroku 
[Deprecated] Project is also designed to be deployed on Heroku.

#### How to SSH to heroku

    $ heroku ps:exec
### Heroku Guide
https://devcenter.heroku.com/articles/dynos

Connect to main app interface. Use `--tail` to persist connection.

    heroku logs --tail

| Actions                         |        Commands           |
|---------------------------------|---------------------------|
| Push code to Heroku from git    |  `git push heroku master` | 
| View Dynos deployed to Heroku   |  `heroku ps`              |
| SSH to Heroku                   |  `heroku ps:exec`         |
| Restart all Dynos	              |  `heroku ps:restart`      |
| Copy file from Heroku           |  `heroku ps:copy FILE`    |
| Environment Variables app env   | `heroku config:set WEB_CONCURRENCY=1` |


