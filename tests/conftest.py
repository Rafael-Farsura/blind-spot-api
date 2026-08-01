import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        yield application
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()
