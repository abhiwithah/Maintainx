# config.py - Application Configuration
# -----------------------------------------------------------
# This file centralizes configuration settings for the MaintainX application.
# It makes it easy to switch between development and production environments.

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class.
    Contains default configuration settings used across the Flask app.
    """
    # Base directory of the project
    BASE_DIR = BASE_DIR

    # SECRET_KEY is used by Flask to securely sign session cookies and flash messages.
    # In production, this should be set in environment variables (.env).
    SECRET_KEY = os.environ.get('SECRET_KEY', 'maintainx-super-secret-key-dev-2026')
    
    # Path to the SQLite database file inside the 'instance' folder
    DATABASE = os.path.join(BASE_DIR, 'instance', 'maintainx.db')
    
    # Debug mode flag
    DEBUG = True
