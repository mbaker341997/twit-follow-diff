# Twitter Follow Diff Site

## To Run
First, activate the virtual environment. On a UNIX system run

`. venv/bin/activate`

This application requires credentials for the twitter API, loaded via python-dotenv. 
Place the following line in a .env file in the project root:

`BEARER_TOKEN=<your_bearer_token>`

Then, run

`flask run`

Server should start on port 5000
