import bleach
import re
from flask import Flask, render_template
from flask_caching import Cache

# Set up a simple cache with a 5 minute timeout and 500 item threshold
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile('settings.py')
    else:
        app.config.from_mapping(test_config)

    # Connect cache to our app
    cache.init_app(app)

    # import follow_diff blueprint
    from . import follow_diff
    app.register_blueprint(follow_diff.bp)
    app.add_url_rule('/', endpoint='index')

    # 404 error handler
    @app.errorhandler(404)
    def not_found_handler(e):
        return render_template('not_found.html')

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
