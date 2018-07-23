import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Yes. I am ready.'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Dev(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        f'sqlite:///{os.path.join(basedir, "data-dev.sqlite")}'


class Prod(Config):
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "data.sqlite")}'


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        f'sqlite:///{os.path.join(basedir, "data-test.sqlite")}'


config = {
    'dev': Dev,
    'testing': Testing,
    'prod': Prod,
    'default': Prod
}
