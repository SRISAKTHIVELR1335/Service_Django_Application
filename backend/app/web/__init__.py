from flask import Blueprint

web_bp = Blueprint('web', __name__)

from app.web import auth_routes, dashboard_routes, tests_routes, logs_routes, downloads_routes
