# blueprints/auth/__init__.py - Authentication Blueprint Setup
# -----------------------------------------------------------
# Blueprints in Flask are a way to organize related routes into distinct modules.
# This blueprint handles user registration, login, and logout.

from flask import Blueprint

# Create the Blueprint named 'auth'
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes so they are registered with the blueprint
from blueprints.auth import routes
