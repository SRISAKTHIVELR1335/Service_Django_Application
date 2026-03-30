from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import auth, vehicles, tests, bundles, versions, logs, settings
