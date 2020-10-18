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

## Improvements
* Pagination and search of results
* Unfollow/Unfriend buttons on each card
* Be able to upload a list of accounts that you don't want to see in the results. 
You already know they don't follow back and you don't care.
* Improved styling. Went with bootstrap to get off the ground but it's very basic
and ugly.
* A favicon.
* A spinner on load (AJAX would be nice but I like the simplicity of the form 
submit to the path).