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


def save_json_to_file(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


# user info api only allows 100 user ids at a time, divide into chunks and pass
def divide_into_chunks(user_ids, chunk_size=100):
    for i in range(0, len(user_ids), chunk_size):
        yield user_ids[i:i+chunk_size]

def save_user_list(user_list, filename):
    chunks = list(divide_into_chunks(user_list))
    data = []
    for chunk in chunks:
        chunk_string = ",".join(str(id) for id in chunk)
        data += get_user_info(chunk_string)
    save_json_to_file(filename, {"data": data})


def main():
    print("Welcome to your Follower Diff!")

    # TODO: be able to authorize other users for this app
    user_name = "amattchronism"
    followers = get_account_list("followers", user_name)
    friends = get_account_list("friends", user_name)
    print("Number of followers: {}".format(len(followers)))
    print("Number you follow: {}".format(len(friends)))

    they_hate_you = list(set(friends) - set(followers))
    you_hate_them = list(set(followers) - set(friends))
    print("Number of accounts you follow and don't follow you back: {}".format(len(they_hate_you)))
    print("Number of accounts who follow you and you don't follow them back: {}".format(len(you_hate_them)))

    # TODO: get each user and produce a file for they_hate_you and you_hate_them
    save_user_list(they_hate_you, "they_hate_you.json")
    save_user_list(you_hate_them, "you_hate_them.json")


if __name__ == "__main__":
    main()
