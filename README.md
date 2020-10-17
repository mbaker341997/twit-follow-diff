# Twitter Follow Diff Site

## To Run
First, activate the virtual environment. On a UNIX system run

`. venv/bin/activate`

Next, you'll need a credentials for the Twitter API. In particular, we
use the bearer token, so run the following command to set the environment variable:

`export BEARER_TOKEN=<your_bearer_token>`

Then, set the FLASK_APP environment variable

`export FLASK_APP=flaskr`

If you want an interactive debugger when exceptions are raised, go ahead and set the
FLASK_ENV environment variable too

`export FLASK_ENV=development`

Then, run

`flask run`

Server should start on port 5000
