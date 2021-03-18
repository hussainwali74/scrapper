
# Requirements 
Python==3.8

#### For Dev testing

#### Instructions to Run

    pip install -r requirements

App runs on port `8000`
Need to specify database credentials in `database.py`
Set environment variables `FIREFOX_BIN` Path to firefox executable,
`GECKODRIVER_PATH` path to geckodriver executable and `DIRECTORY_PATH `
path to directory where images directories will be saved.

##### Starting Web Server
    
    ./run_server.sh

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
