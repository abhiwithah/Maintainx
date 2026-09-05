# blueprints/auth/utils.py - Authentication Helpers & Decorators
# -----------------------------------------------------------
# This module provides reusable security decorators for route protection.
#
# Key Concepts for Beginners:
# 1. Python Decorators (@login_required):
#    A decorator wraps a route function. Before running the actual view, it checks
#    if the visitor has an active session. If not, it redirects them to the login page.
# 2. functools.wraps:
#    Preserves the original function's name and docstring so Flask routing works properly.

from functools import wraps
from flask import session, redirect, url_for, flash, request
from models.user import User

def login_required(view_func):
    """
    Decorator to protect routes from unauthenticated access.
    
    If the user is logged in (session has 'user_id'), the view function executes normally.
    If the user is NOT logged in, redirects to the login page with a message and stores
    the requested URL in the 'next' parameter so they return there after logging in.
    
    Usage:
        @user_bp.route('/dashboard')
        @login_required
        def dashboard():
            ...
    """
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        # Check if user_id exists in the current session
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            # Redirect to the login route with a 'next' query parameter
            return redirect(url_for('auth.login', next=request.url))
        return view_func(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator to restrict route access to specific roles (e.g. 'admin', 'staff').
    
    Usage:
        @admin_bp.route('/admin')
        @role_required('admin')
        def admin_panel():
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role', 'user')
            if user_role not in allowed_roles:
                flash('You do not have permission to view this resource.', 'danger')
                return redirect(url_for('user.dashboard'))
                
            return view_func(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """
    Retrieve the full database record for the currently logged-in user.
    
    Returns:
        sqlite3.Row or None: Current user row if logged in, else None.
    """
    user_id = session.get('user_id')
    if user_id:
        return User.get_by_id(user_id)
    return None
