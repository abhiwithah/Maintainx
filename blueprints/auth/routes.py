# blueprints/auth/routes.py - Authentication Routes (Register, Login, Logout)
# -----------------------------------------------------------------------------
# This module defines the view functions for user authentication.
#
# Beginner Flow Explanation:
# 1. Registration:
#    HTML Form (POST) -> Flask request.form -> Validation -> Password Hashing
#    -> db.session / User.create() -> Flash success -> Redirect to Login.
#
# 2. Login:
#    HTML Form (POST) -> Flask request.form -> Lookup User by Email
#    -> Verify Hash via check_password_hash() -> Set Flask session['user_id']
#    -> Redirect to User Dashboard (/user/dashboard).
#
# 3. Logout:
#    GET /auth/logout -> session.clear() -> Flash message -> Redirect to Home (/).

import re
from flask import render_template, request, redirect, url_for, flash, session
from blueprints.auth import auth_bp
from models.user import User

# Simple regex pattern for validating email address format
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

# =============================================================================
# ROUTE 1: USER REGISTRATION
# URL: /auth/register
# Methods: GET (display form) | POST (process submitted form)
# =============================================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user account registration.
    
    GET: Renders the registration form template (templates/auth/register.html).
    POST: Extracts form inputs, validates fields, checks for duplicate email,
          hashes the password, saves to the database, and redirects to login.
    """
    # If the user is already logged in, redirect them directly to the user dashboard
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        # 1. Retrieve data submitted from the HTML <form> via request.form
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'user') # Default role is 'user'

        # 2. Server-side validation
        if not name:
            flash('Please enter your full name.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        if not email or not re.match(EMAIL_REGEX, email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please verify.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        # 3. Check if user already exists in the database
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('An account with this email address already exists. Please log in.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        # 4. Hash password and save new user in the SQLite database
        try:
            new_user_id = User.create(name=name, email=email, password=password, role=role)
            flash('Account created successfully! You can now log in.', 'success')
            # Redirect to the login route
            return redirect(url_for('auth.login'))
        except Exception as e:
            # Handle database errors gracefully without crashing the app
            flash('An unexpected error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

    # GET request: render the empty registration form
    return render_template('auth/register.html')


# =============================================================================
# ROUTE 2: USER LOGIN
# URL: /auth/login
# Methods: GET (display form) | POST (process credentials)
# =============================================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user authentication and session creation.
    
    GET: Renders the login page template (templates/auth/login.html).
    POST: Validates credentials against stored password hash. On success,
          stores user ID and name in session cookie and redirects to dashboard.
    """
    # If already logged in, redirect directly to dashboard
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        # Retrieve input from login form
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Validate input presence
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html', email=email)

        # Look up the user record by email
        user = User.get_by_email(email)

        # Check if user exists and verify password against the cryptographic hash
        if user and User.verify_password(user['password_hash'], password):
            # Session authentication: store key identity values in Flask session
            session.clear() # Clear any previous stale session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['role'] = user['role']

            flash(f"Welcome back, {user['name']}!", 'success')

            # If user was redirected from a protected page, return them there
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            # Default redirect: Authenticated User Module Dashboard
            return redirect(url_for('user.dashboard'))
        else:
            # Generic error message to prevent username enumeration attacks
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

    # GET request: render login form
    return render_template('auth/login.html')


# =============================================================================
# ROUTE 3: USER LOGOUT
# URL: /auth/logout
# Methods: GET
# =============================================================================
@auth_bp.route('/logout')
def logout():
    """
    Logs out the current user by clearing the session dictionary.
    Redirects back to the public homepage (/).
    """
    # session.clear() removes all stored cookies/session keys
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))
