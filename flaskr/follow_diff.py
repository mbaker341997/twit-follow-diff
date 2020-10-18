from flask import (
    Blueprint, current_app, render_template, request
)
from . import cache
import requests

from .errors import *

bp = Blueprint('follow_diff', __name__)

USERNAME_KEY = 'username'
TYPE_KEY = 'type'
HATERS_TYPE = 'haters'
VICTIMS_TYPE = 'victims'
FOLLOWERS_KEY = "followers"
FRIENDS_KEY = "friends"
BASE_TEMPLATE = 'base.html'
RESULT_TEMPLATE = 'result.html'
MAX_ACCOUNT_NUM = 5000
ACCOUNT_LIST_API_URL = "https://api.twitter.com/1.1/{}/ids.json?screen_name={}"
USER_INFO_API_URL = "https://api.twitter.com/2/users?ids={}&user.fields=description,profile_image_url"


@bp.route("/")
def index():
    return render_template(BASE_TEMPLATE)


@bp.route("/diff")
def diff():
    username = request.args.get(USERNAME_KEY)
    account_type = request.args.get(TYPE_KEY)
    errors = []

    # validate parameters
    if not username:
        errors.append(MISSING_USERNAME_ERROR_MESSAGE)
    if not account_type:
        errors.append(MISSING_TYPE_ERROR_MESSAGE)
    elif account_type != HATERS_TYPE and account_type != VICTIMS_TYPE:
        errors.append(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE)
    if len(errors) > 0:
        return render_template(BASE_TEMPLATE, errors=errors)

    try:
        # Retrieve friends and followers from twitter api
        friends_and_followers = get_friends_and_followers(username)

        # Render error if we reach our account number limit
        if len(friends_and_followers[FRIENDS_KEY]) >= MAX_ACCOUNT_NUM:
            errors.append(TOO_MANY_FOLLOWS_ERROR_MESSAGE)
        if len(friends_and_followers[FOLLOWERS_KEY]) >= MAX_ACCOUNT_NUM:
            errors.append(TOO_MANY_FOLLOWERS_ERROR_MESSAGE)

        # Run diff on friends and followers
        friends_set = set(friends_and_followers[FRIENDS_KEY])
        followers_set = set(friends_and_followers[FOLLOWERS_KEY])
        they_hate_you = list(friends_set - followers_set)
        you_hate_them = list(followers_set - friends_set)
        result = []

        # Decide which list to render
        if account_type == HATERS_TYPE:
            result = they_hate_you
        elif account_type == VICTIMS_TYPE:
            result = you_hate_them

        # Render the result
        return render_template(RESULT_TEMPLATE, username=username, account_type=account_type,
                               followers_count=len(followers_set), friends_count=len(friends_set),
                               haters_count=len(they_hate_you), victims_count=len(you_hate_them),
                               result=get_user_list(result), errors=errors)

    # TODO: maybe combine these into an API Error and just send apiErr.message?
    except BadUserError as badUserErr:
        return render_template(BASE_TEMPLATE, username=username, account_type=account_type, errors=[badUserErr.message])
    except RateLimitExceededError as rateLimitErr:
        return render_template(BASE_TEMPLATE, username=username, account_type=account_type, errors=[rateLimitErr.message])
    except Exception as randomEx:
        print(randomEx)
        return render_template(BASE_TEMPLATE, username=username, account_type=account_type,
                               errors=[GENERIC_ERROR_MESSAGE_FOR_FRONTEND])


def get_bearer_token_header():
    headers = {"Authorization": "Bearer {}".format(current_app.config['BEARER_TOKEN'])}
    return headers


# Note: we memoize instead of just cache because the arguments matter for what we're retrieving
@cache.memoize()
def get_account_list(account_type, display_name):
    # just grabbing ids cuz it's simpler to run the diff + fewer requests needed to get all the users
    url = ACCOUNT_LIST_API_URL.format(account_type, display_name)
    print("Requesting {} for user: {}".format(account_type, display_name))

    response = requests.request("GET", url, headers=get_bearer_token_header())
    if response.status_code == 401:
        print(response.text)
        raise BadUserError(
            display_name, NOT_AUTHORIZED_FOR_USER_TEMPLATE.format(account_type, display_name)
        )
    elif response.status_code == 404:
        print(response.text)
        raise BadUserError(
            display_name, USER_NOT_FOUND_TEMPLATE.format(display_name)
        )
    elif response.status_code == 429:
        print(response.text)
        raise RateLimitExceededError(RATE_LIMIT_ON_ACCOUNT_LIST_TEMPLATE.format(account_type, display_name))
    elif response.status_code != 200:
        raise Exception(
            GENERIC_ERROR_TEMPLATE.format(
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


@cache.memoize()
def get_user_info(user_ids):
    url = USER_INFO_API_URL.format(user_ids)
    print("Retrieving profile information for users: {}".format(user_ids))
    response = requests.request("GET", url, headers=get_bearer_token_header())
    if response.status_code == 429:
        print(response.text)
        raise RateLimitExceededError("Unable to retrieve user information. Twitter is rate limiting us. "
                                     "Try again in ~15 minutes")
    elif response.status_code != 200:
        raise Exception(
            GENERIC_ERROR_TEMPLATE.format(
                response.status_code, response.text
            )
        )
    return response.json()["data"]


# user info api only allows 100 user ids at a time, divide into chunks and pass
# TODO: idea, we pick out and cache accounts we've seen before. we make the request in batches but
#  we could strategize which ones we batch?
def divide_into_chunks(user_ids, chunk_size=100):
    for i in range(0, len(user_ids), chunk_size):
        yield user_ids[i:i+chunk_size]


def get_user_list(user_list):
    chunks = list(divide_into_chunks(user_list))
    data = []
    for chunk in chunks:
        chunk_string = ",".join(str(user_id) for user_id in chunk)
        data += get_user_info(chunk_string)
    return {'accounts': data}
