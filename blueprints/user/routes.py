# blueprints/user/routes.py - Protected User Module Routes
# -----------------------------------------------------------------------------
# This module provides all views for authenticated users to manage maintenance
# requests. Every route in this module is protected by the @login_required decorator.
#
# Beginner Flow Explanation:
# 1. User visits /user/dashboard:
#    @login_required checks session['user_id'].
#    If valid, queries Complaint.get_user_stats() and renders user/dashboard.html.
# 2. User submits complaint at /user/submit:
#    Form (POST) -> Complaint.create(user_id, title, category, description, location, priority)
#    -> Stored in SQLite -> Redirects to /user/complaints.

from flask import render_template, request, redirect, url_for, flash, session, abort
from blueprints.user import user_bp
from blueprints.auth.utils import login_required
from models.complaint import Complaint
from models.user import User

# =============================================================================
# ROUTE 1: USER DASHBOARD
# URL: /user/dashboard
# Methods: GET
# =============================================================================
@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Renders the main authenticated dashboard for regular users.
    Displays quick stat counters (Total, Pending, In Progress, Resolved)
    and a table of the 5 most recent maintenance requests.
    """
    user_id = session['user_id']
    
    # Fetch user account details
    user = User.get_by_id(user_id)
    
    # Calculate ticket counts for dashboard metrics
    stats = Complaint.get_user_stats(user_id)
    
    # Get recent complaints (up to 5)
    recent_complaints = Complaint.get_recent_by_user(user_id, limit=5)
    
    return render_template(
        'user/dashboard.html',
        user=user,
        stats=stats,
        recent_complaints=recent_complaints
    )


# =============================================================================
# ROUTE 2: SUBMIT MAINTENANCE REQUEST
# URL: /user/submit
# Methods: GET (display form) | POST (save complaint to database)
# =============================================================================
@user_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    """
    Allows an authenticated user to submit a new maintenance complaint.
    
    GET: Displays the submission form with category and priority selections.
    POST: Validates inputs, saves the complaint to SQLite via Complaint.create(),
          and redirects the user to their complaints list.
    """
    user_id = session['user_id']

    if request.method == 'POST':
        # Retrieve form data from request.form
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        location = request.form.get('location', '').strip()
        priority = request.form.get('priority', 'Medium').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not title or not category or not location or not description:
            flash('Please complete all required fields.', 'danger')
            return render_template(
                'user/submit_complaint.html',
                title=title,
                category=category,
                location=location,
                priority=priority,
                description=description
            )

        # Insert new complaint into SQLite
        try:
            complaint_id = Complaint.create(
                user_id=user_id,
                title=title,
                category=category,
                description=description,
                location=location,
                priority=priority
            )
            flash('Maintenance request submitted successfully! Our team has been notified.', 'success')
            return redirect(url_for('user.my_complaints'))
        except Exception as e:
            flash('Failed to submit maintenance request. Please try again.', 'danger')
            return render_template('user/submit_complaint.html')

    # GET request: render the blank submission form
    return render_template('user/submit_complaint.html')


# =============================================================================
# ROUTE 3: MY COMPLAINTS LIST
# URL: /user/complaints
# Methods: GET
# =============================================================================
@user_bp.route('/complaints')
@login_required
def my_complaints():
    """
    Displays a filterable list of all complaints submitted by the current user.
    Supports filtering by status query parameter: ?status=Pending, etc.
    """
    user_id = session['user_id']
    status_filter = request.args.get('status', 'All')

    # Fetch matching complaints for this user
    complaints = Complaint.get_by_user_id(user_id, status_filter=status_filter)
    
    # Fetch stats for tab counters
    stats = Complaint.get_user_stats(user_id)

    return render_template(
        'user/my_complaints.html',
        complaints=complaints,
        current_status=status_filter,
        stats=stats
    )


# =============================================================================
# ROUTE 4: COMPLAINT DETAILS
# URL: /user/complaint/<id>
# Methods: GET
# =============================================================================
@user_bp.route('/complaint/<int:complaint_id>')
@login_required
def complaint_details(complaint_id):
    """
    Displays full details and status history of a single maintenance complaint.
    Ensures that regular users can only view their own complaints.
    """
    user_id = session['user_id']
    user_role = session.get('role', 'user')

    # If user is regular user, restrict lookup to their own user_id
    filter_user_id = None if user_role in ['admin', 'staff'] else user_id
    complaint = Complaint.get_by_id(complaint_id, user_id=filter_user_id)

    if not complaint:
        flash('Complaint not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('user.my_complaints'))

    return render_template('user/complaint_details.html', complaint=complaint)
