from flask import Flask
from flask_cors import CORS
from config import Config
from app.extensions import db, cache, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    from app.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app
