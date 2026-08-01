import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-blind-spot-local")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///"
        + os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "blindspot.db",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
