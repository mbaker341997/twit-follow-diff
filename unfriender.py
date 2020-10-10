import requests
import os
import json

def auth():
    print("Authorizing!")
    return os.environ.get("BEARER_TOKEN")


def get_bearer_token_header():
    headers = {"Authorization": "Bearer {}".format(auth())}
    return headers


def get_account_list(account_type, display_name):
    url = "https://api.twitter.com/1.1/{}/ids.json?screen_name={}".format(account_type, display_name)
    print("Requesting {} for user: {}".format(account_type, display_name))

    # TODO: pagination?
    response = requests.request("GET", url, headers=get_bearer_token_header())
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    response_json = response.json()
    return response_json["ids"]

def main():
    print("Welcome to your Follower Diff!")

    # TODO: be able to authorize other users for this app
    user_name = "amattchronism"
    followers = get_account_list("followers", user_name)
    friends = get_account_list("friends", user_name)
    print("Number of followers: {}".format(len(followers)))
    print("Number you follow: {}".format(len(friends)))

    they_hate_you = set(friends) - set(followers)
    you_hate_them = set(followers) - set(friends)
    print("Number of accounts you follow and don't follow you back: {}".format(len(they_hate_you)))
    print("Number of accounts who follow you and you don't follow them back: {}".format(len(you_hate_them)))

if __name__ == "__main__":
    main()
