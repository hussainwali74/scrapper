
# Requirements 
Python==3.8

#### For Dev testing

#### Instructions to Run

    pip install -r requirements

App runs on port `8000`
Need to specify database credentials in `database.py`
Set environment variables `FIREFOX_BIN` Path to firefox executable,
`GECKODRIVER_PATH` path to geckodriver executable.

##### Starting Web Server
    
    ./run_server.sh

##### Instructions on crontab
You need curl for this.
In crontab paste the following command to run code at 00:30 every
night.

    30 0 * * * /<path_to_project_directory>/run_add_cars.sh

Here first number is minutes, second is hours.

Where <path_to_project_directory> is your local path to project.
### Heroku 
Project is designed to be deployed on Heroku.

#### How to SSH to heroku

    $ heroku ps:exec

### Features / things done
##### Resources:
https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f


    INTEGER1 -eq INTEGER2
         INTEGER1 is equal to INTEGER2

    INTEGER1 -ge INTEGER2
         INTEGER1 is greater than or equal to INTEGER2

    INTEGER1 -gt INTEGER2
         INTEGER1 is greater than INTEGER2

    INTEGER1 -le INTEGER2
         INTEGER1 is less than or equal to INTEGER2

    INTEGER1 -lt INTEGER2
        INTEGER1 is less than INTEGER2

    INTEGER1 -ne INTEGER2
        INTEGER1 is not equal to INTEGER2

### Heroku Guide
https://devcenter.heroku.com/articles/dynos

##### Others

Old procfile contents

    web: ENV="prod" uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}

Connect to main app interface. Use `--tail` to persist connection.

    heroku logs --tail

Push code to Heroku from git       `git push heroku master`
View Dynos deployed to Heroku      `heroku ps`
SSH to Heroku                      `heroku ps:exec`
Restart all Dynos	               `heroku ps:restart`

#### Sample queries
http://localhost:8000/car/search?price_ge=26_000&mileage_le=5_000&limit=100

