from flask import Flask
from flasgger import Swagger

from app.config import Config
from app.extensions import db, cors


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # file:// manda Origin: null — precisa liberar senão o SPA morre no browser
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
    )
    db.init_app(app)

    app.config["SWAGGER"] = {
        "title": "Blind Spot API",
        "uiversion": 3,
        "specs_route": "/api/docs/",
    }
    Swagger(app)

    # importa models para o metadata do SQLAlchemy
    from app import models  # noqa: F401
    from app.api.health import bp as health_bp

    app.register_blueprint(health_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
