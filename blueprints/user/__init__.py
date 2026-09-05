# blueprints/user/__init__.py - User Blueprint Setup
# -----------------------------------------------------------
# This blueprint contains protected routes for authenticated regular users:
# - Dashboard overview
# - Submitting maintenance requests
# - Viewing and filtering my maintenance complaints
# - Inspecting complaint status details

from flask import Blueprint

# Create blueprint with /user prefix
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Import routes to register them with the blueprint
from blueprints.user import routes
