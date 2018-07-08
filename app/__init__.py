from flask import Flask

from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from .blog.presentation import blog
    app.register_blueprint(blog)

    return app
