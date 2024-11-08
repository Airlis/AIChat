from flask import Flask
from config import Config
from app.extensions import db, migrate, cache, cors
from app.api import api_blueprint

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    cors.init_app(app)

    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
