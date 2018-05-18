import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Yes. I am ready.'
    DEBUG = False
    TESTING = False


class Dev(Config):
    DEBUG = True


class Prod(Config):
    pass


class Testing(Config):
    TESTING = True


config = {
    'dev': Dev,
    'testing': Testing,
    'prod': Prod,
    'default': Prod
}
