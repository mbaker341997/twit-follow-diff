import requests
import os
import json
from flask import Flask
app = Flask(__name__)

FOLLOWERS_KEY = "followers"
FRIENDS_KEY = "friends"

@app.route('/')
def index():
    return 'Index Page'


@app.route('/haters/<username>')
def get_haters(username):
    followers = get_account_list("followers", user_name)
    friends = get_account_list("friends", user_name)
    they_hate_you = list(set(friends) - set(followers))
    return get_user_list(you_hate_them)


@app.route('/victims/<username>')
def get_victims(username):
    friends_and_followers = get_friends_and_followers(username)
    you_hate_them = list(set(friends_and_followers[FOLLOWERS_KEY]) - set(friends_and_followers[FRIENDS_KEY]))
    return get_user_list(you_hate_them)


# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
def get_bearer_token_header():
    headers = {"Authorization": "Bearer {}".format(os.environ.get("BEARER_TOKEN"))}
    return headers


def get_account_list(account_type, display_name):
    # just grabbing ids cuz it's simpler to run the diff
    url = "https://api.twitter.com/1.1/{}/ids.json?screen_name={}".format(account_type, display_name)
    print("Requesting {} for user: {}".format(account_type, display_name))

    response = requests.request("GET", url, headers=get_bearer_token_header())
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    response_json = response.json()
    return response_json["ids"]


def get_friends_and_followers(username):
    return {
        FOLLOWERS_KEY: get_account_list(FOLLOWERS_KEY, username),
        FRIENDS_KEY: get_account_list(FRIENDS_KEY, username)
    }


def get_user_info(user_ids):
    user_fields = "description"
    url = "https://api.twitter.com/2/users?ids={}&user.fields={}".format(user_ids, user_fields)
    print("Requesting info for users: {}".format(user_ids))
    response = requests.request("GET", url, headers=get_bearer_token_header())
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()["data"]


# user info api only allows 100 user ids at a time, divide into chunks and pass
def divide_into_chunks(user_ids, chunk_size=100):
    for i in range(0, len(user_ids), chunk_size):
        yield user_ids[i:i+chunk_size]


def get_user_list(user_list):
    chunks = list(divide_into_chunks(user_list))
    data = []
    for chunk in chunks:
        chunk_string = ",".join(str(id) for id in chunk)
        data += get_user_info(chunk_string)
    return {"data": data}
