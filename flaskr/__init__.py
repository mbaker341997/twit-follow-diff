import bleach
import re
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is not None:
        app.config.from_mapping(test_config)

    # import follow_diff blueprint
    from . import follow_diff
    app.register_blueprint(follow_diff.bp)
    app.add_url_rule('/', endpoint='index')

    # filter for linkifying
    @app.template_filter('linkify')
    def linkify_filter(s):
        return bleach.linkify(s)

    def sub_username(username_matchobj):
        username_string = username_matchobj.group(0)
        return '<a href="https://twitter.com/{}">{}</a>'.format(username_string[1:], username_string)

    # filter for converting twitter username @s to links
    @app.template_filter('usernamify')
    def username_filter(s):
        # regex from https://stackoverflow.com/questions/2304632/regex-for-twitter-username
        return re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)', sub_username, s)

    return app
