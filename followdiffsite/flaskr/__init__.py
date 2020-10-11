import os

from flask import Flask

def create_app():
    app = Flask(__name__)

    # import follow_diff blueprint
    from . import follow_diff
    app.register_blueprint(follow_diff.bp)
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
