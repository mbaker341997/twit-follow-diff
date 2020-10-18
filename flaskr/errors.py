MISSING_USERNAME_ERROR_MESSAGE = 'Username is required.'
MISSING_TYPE_ERROR_MESSAGE = 'Type is required.'
INVALID_ACCOUNT_TYPE_ERROR_MESSAGE = 'Invalid account type.'
TOO_MANY_FOLLOWS_ERROR_MESSAGE = 'Unable to retrieve all the accounts this one follows. Results likely inaccurate.'
TOO_MANY_FOLLOWERS_ERROR_MESSAGE = 'Unable to retrieve all the followers of this account. Results likely inaccurate.'


class Error(Exception):
    """Base class for other exceptions"""
    pass


class BadUserError(Error):
    """Exception raised when Twitter does not allow us to retrieve the user's info by name.
    If could be because they're private or that username is invalid.

    Attributes:
        username -- the twitter user for which we're not authorized.
        message -- error message.
    """

    def __init__(self, username, message):
        self.username = username
        self.message = message


class RateLimitExceededError(Error):
    """Exception raised when we exceed our rate limit with the Twitter API!"""

    def __init__(self, message):
        self.message = message
