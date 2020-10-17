from flask import Flask
import bleach


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

    return app
