# app.py - Main Flask Application Entry Point
# -----------------------------------------------------------------------------
# MaintainX: Clean, Editorial Maintenance Operations Platform
#
# This file initializes the Flask application, loads configuration,
# sets up the SQLite database, registers blueprints (auth, user),
# defines public website routes, and provides template context helpers.

from flask import Flask, render_template, session, jsonify
from config import Config
from database import db
from blueprints.auth import auth_bp
from blueprints.user import user_bp

# 1. Initialize Flask App
app = Flask(__name__)

# 2. Load Configuration from config.py
app.config.from_object(Config)

# 3. Initialize Database Connection & Tables
db.init_app(app)

# 4. Register Modular Blueprints
# Authentication Blueprint (Login, Register, Logout)
app.register_blueprint(auth_bp)

# User Module Blueprint (Dashboard, Complaints, Tickets)
app.register_blueprint(user_bp)


# =============================================================================
# CONTEXT PROCESSORS & TEMPLATE HELPERS
# =============================================================================
@app.context_processor
def inject_auth_user():
    """
    Injects authentication state into every Jinja2 template automatically.
    This allows templates to check `if is_authenticated:` and access `current_user_name`.
    """
    user_id = session.get('user_id')
    return {
        'is_authenticated': user_id is not None,
        'current_user_id': user_id,
        'current_user_name': session.get('user_name', ''),
        'current_user_role': session.get('role', 'user')
    }


@app.template_filter('format_date')
def format_date_filter(val):
    """Formats date/timestamp values cleanly for template display."""
    if not val:
        return 'N/A'
    val_str = str(val)
    # Return YYYY-MM-DD or slice first 10 characters
    return val_str[:10]


# =============================================================================
# PUBLIC WEBSITE ROUTES (Editorial Front-Facing Pages)
# =============================================================================

@app.route('/')
def home():
    """
    Public Homepage:
    Presents the MaintainX editorial landing page, problem/solution breakdown,
    how it works workflow (Report -> Assign -> Track -> Resolve), capabilities,
    and calls-to-action for Get Started and Login.
    """
    return render_template('index.html')


@app.route('/features')
def features():
    """
    Public Features Page:
    Comprehensive overview of platform capabilities: ticket dispatch, real-time
    status tracking, equipment logs, and operational transparency.
    """
    return render_template('features.html')


@app.route('/how-it-works')
def how_it_works():
    """
    Public How It Works Page:
    Step-by-step breakdown of the maintenance lifecycle.
    """
    return render_template('how_it_works.html')


@app.route('/about')
def about():
    """
    Public About Page:
    The story, mission, and architectural philosophy of MaintainX.
    """
    return render_template('about.html')


# =============================================================================
# DIAGNOSTIC & HEALTH-CHECK ROUTES
# =============================================================================

@app.route('/test')
def test_route():
    """Simple health-check confirming Flask and database are active."""
    return jsonify({
        "status": "ok",
        "app": "MaintainX",
        "version": "1.0.0",
        "message": "Flask application is running smoothly."
    })


@app.route('/test/routes')
def list_routes():
    """
    Lists all registered routes in the application.
    Useful for inspecting blueprints and URL mapping.
    """
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "url": rule.rule,
            "methods": sorted(rule.methods)
        })
    routes.sort(key=lambda r: r["url"])
    return jsonify({
        "total_routes": len(routes),
        "routes": routes
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Render a clean 404 error page."""
    return render_template('base.html', error_title="404 - Page Not Found", 
                           error_message="The page you requested does not exist or has been moved."), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Render a friendly 500 error page."""
    return render_template('base.html', error_title="500 - Internal Server Error", 
                           error_message="An unexpected error occurred. Please try again later."), 500


# =============================================================================
# APPLICATION RUNNER
# =============================================================================
if __name__ == '__main__':
    # Runs the local development server with auto-reloading
    app.run(debug=True, host='127.0.0.1', port=5000)