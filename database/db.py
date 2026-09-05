# database/db.py - SQLite Database Helper
# -----------------------------------------------------------
# This module provides simple helper functions to connect to, initialize,
# and query the SQLite database.
#
# Beginner Notes:
# - SQLite stores data in a single file on disk (instance/maintainx.db).
# - Flask uses the global object `g` (from flask import g) to hold variables
#   that are unique to a single incoming HTTP request.
# - We store the database connection in `g` so we don't open multiple connections
#   during one request.

import sqlite3
import os
from flask import g, current_app

def get_db():
    """
    Get or create a database connection for the current request.
    
    Returns:
        sqlite3.Connection: Active SQLite database connection.
    """
    # Check if a database connection already exists in Flask's request context `g`
    if 'db' not in g:
        # Connect to the SQLite database specified in app config
        db_path = current_app.config['DATABASE']
        
        # Ensure the parent directory (e.g. 'instance') exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(db_path)
        
        # Row factory allows accessing query results by column name, e.g. row['email']
        # like a Python dictionary instead of numeric tuples like row[0].
        g.db.row_factory = sqlite3.Row
        
        # Enable SQLite Foreign Keys support
        g.db.execute("PRAGMA foreign_keys = ON;")

    return g.db


def close_db(e=None):
    """
    Close the database connection at the end of the request.
    Flask calls this automatically thanks to app.teardown_appcontext.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Initialize the database by executing database/schema.sql.
    Creates tables if they do not exist.
    """
    db = get_db()
    # Read the SQL schema file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, mode='r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    """
    Register database functions with the Flask application.
    
    1. Tells Flask to call close_db() when cleaning up after returning a response.
    2. Initializes tables automatically on first launch if they do not exist.
    """
    app.teardown_appcontext(close_db)
    
    # Initialize the database within application context on startup
    with app.app_context():
        init_db()
