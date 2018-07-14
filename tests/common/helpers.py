import pytest

from app import create_app
from app.common.adapter.repository.sql import db


class FlaskAppEnvironment(object):
    @pytest.fixture(scope='class')
    def app(self):
        return create_app('testing')


class FlaskAppContextEnvironment(FlaskAppEnvironment):
    @pytest.fixture(autouse=True)
    def app_context(self, app):
        app_context = app.app_context()
        app_context.push()
        yield
        app_context.pop()


class SqlEnvironment(FlaskAppContextEnvironment):
    @pytest.fixture(autouse=True)
    def table(self, request):
        db.create_all()

        def fin():
            db.session.remove()
            db.drop_all()

        request.addfinalizer(fin)
