class Error(Exception):
    """Base class for other exceptions"""
    pass


class NotAuthorizedForUserError(Error):
    """Exception raised when Twitter does not allow us to retrieve the user's info

    Attributes:
        username -- the twitter user for which we're not authorized.
        message -- error message.
    """

    def __init__(self, username, message):
        self.username = username
        self.message = message