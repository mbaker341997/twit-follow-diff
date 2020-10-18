from flaskr.follow_diff import *

TEST_USER = "dummy_user"


def test_index(client):
    response = client.get('/')
    # Make sure we have the main ideas -> explanation of what the app is and the username input
    # response.data returns bytes so compare bytes to bytes
    assert b'TwitDiff' in response.data
    assert b'See who doesn\'t follow you back.' in response.data
    assert b'Also see who you don\'t follow back.' in response.data
    assert b'<input name="username"' in response.data
    assert_no_errors(response)


def test_diff_no_params_returns_errors(client):
    response = client.get('/diff')
    # two errors, one for no username, the other for no type
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) in response.data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) in response.data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) not in response.data


def test_diff_invalid_account_type_returns_error(client):
    response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, 'invalidType'))
    # only an error for invalid type
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) not in response.data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) not in response.data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) in response.data

# happy case simple

# happy case linkify

# happy case linkify twitter username

# happy case don't linkify email

# happy case more than one chunk? (if this is too much effort then don't bother)

# 401 error on get account list

# 404 error on get account list

# 429 error on get account list

# 500 random error on get account list

# 429 error on get user info

# 500 random error on get account list

def assert_no_errors(response):
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) not in response.data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) not in response.data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) not in response.data