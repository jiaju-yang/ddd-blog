from flask import Flask

from config import config
from .common.adapter.repository.sql import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .blog.presentation import blog
    app.register_blueprint(blog)

    return app
