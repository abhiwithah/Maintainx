# app.py - Main Flask application entry point
# -----------------------------------------------
# This file creates the Flask app and registers routes/blueprints.

from flask import Flask, jsonify  # Flask: web framework | jsonify: turns dicts into JSON responses

# Create the Flask application instance
app = Flask(__name__)

# -----------------------------------------------
# FUTURE: Register your blueprints here once they are ready.
# Example:
#   from blueprints.auth.routes import auth_bp
#   app.register_blueprint(auth_bp, url_prefix='/auth')
# -----------------------------------------------


# == Diagnostic Route 1 ==========================
# GET /test
# Simple health-check: confirms Flask is running.
# No authentication needed -- just for testing.
@app.route('/')
def test_route():
    # Return a JSON response with status and a message
    return jsonify({
        "status": "ok",
        "message": "Flask is running"
    })


# == Diagnostic Route 2 ==========================
# GET /test/routes
# Lists every URL route registered in the app,
# including the HTTP methods allowed for each.
# Useful to confirm that blueprints are connected.
@app.route('/test/routes')
def list_routes():
    routes = []  # We will collect route info into this list

    # app.url_map contains all registered URL rules
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,        # Internal name of the view function
            "url": rule.rule,                 # The URL pattern, e.g. "/test/routes"
            "methods": sorted(rule.methods)   # HTTP methods like GET, POST, etc.
        })

    # Sort alphabetically by URL for easy reading
    routes.sort(key=lambda r: r["url"])

    return jsonify({
        "total_routes": len(routes),
        "routes": routes
    })


# == Run the app =================================
# This block only runs when you execute this file directly:
#   python app.py
# It will NOT run when imported by another module.
if __name__ == '__main__':
    # debug=True -> auto-reloads on code changes and shows detailed error pages
    app.run(debug=True)