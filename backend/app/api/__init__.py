from flask import Blueprint
from flask_restx import Api

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint, title='Visitor Classification API', version='1.0', description='API for visitor classification')

from app.api import api_endpoints
