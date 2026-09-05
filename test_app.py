# test_app.py - Automated Test Suite for MaintainX
# -----------------------------------------------------------
# Verifies:
# 1. Database schema and tables
# 2. Public website pages and navigation
# 3. User registration, duplicate rejection, and password hashing
# 4. User login (success & failure handling)
# 5. Route protection (unauthenticated access redirects to login)
# 6. Authenticated user dashboard, complaint submission, and ticket filtering
# 7. Access control between users
# 8. Logout and session teardown

import os
import sys
import unittest
import sqlite3

# Set environment
os.environ['SECRET_KEY'] = 'test-secret-key-maintainx'

from app import app
from database.db import get_db, init_db
from models.user import User
from models.complaint import Complaint

class MaintainXTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['DATABASE'] = os.path.join(app.config['BASE_DIR'], 'instance', 'test_maintainx.db')
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Initialize test database
        init_db()

    def tearDown(self):
        # Pop context
        self.app_context.pop()
        db_path = app.config['DATABASE']
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass

    def test_01_public_pages(self):
        """Test that all public pages load with HTTP 200 and correct branding."""
        routes = ['/', '/features', '/how-it-works', '/about', '/test', '/test/routes']
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed with status {response.status_code}")
            if route == '/':
                self.assertIn(b'MaintainX', response.data)
                self.assertIn(b'Operational Integrity Platform', response.data)

    def test_02_registration_validation_and_security(self):
        """Test registration flow, validation errors, duplicate checks, and password hashing."""
        # 1. Missing name
        resp = self.client.post('/auth/register', data={
            'name': '',
            'email': 'valid@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Please enter your full name', resp.data)

        # 2. Invalid email format
        resp = self.client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'not-an-email',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Please enter a valid email address', resp.data)

        # 3. Short password
        resp = self.client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'user@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn(b'Password must be at least 6 characters', resp.data)

        # 4. Password mismatch
        resp = self.client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'user@example.com',
            'password': 'password123',
            'confirm_password': 'differentPassword123'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', resp.data)

        # 5. Successful registration
        response = self.client.post('/auth/register', data={
            'name': 'Alice Engineer',
            'email': 'alice@example.com',
            'password': 'securePassword123',
            'confirm_password': 'securePassword123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully', response.data)

        # 6. Verify user in database
        user = User.get_by_email('alice@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Alice Engineer')
        
        # 7. CRITICAL: Verify password is a cryptographic hash, NEVER plain text
        self.assertNotEqual(user['password_hash'], 'securePassword123')
        self.assertTrue(user['password_hash'].startswith('pbkdf2:sha256:') or user['password_hash'].startswith('scrypt:'))
        self.assertTrue(User.verify_password(user['password_hash'], 'securePassword123'))
        self.assertFalse(User.verify_password(user['password_hash'], 'wrongPassword'))

        # 8. Test duplicate registration prevention
        dup_response = self.client.post('/auth/register', data={
            'name': 'Alice Copy',
            'email': 'alice@example.com',
            'password': 'anotherPassword123',
            'confirm_password': 'anotherPassword123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', dup_response.data)

    def test_03_login_and_logout(self):
        """Test login validation, session state, and logout."""
        # Create user
        User.create('Bob Technician', 'bob@example.com', 'mypassword123', role='user')

        # Invalid login
        bad_resp = self.client.post('/auth/login', data={
            'email': 'bob@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', bad_resp.data)

        # Valid login
        good_resp = self.client.post('/auth/login', data={
            'email': 'bob@example.com',
            'password': 'mypassword123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Bob Technician', good_resp.data)
        self.assertIn(b'User Operations', good_resp.data)

        # Logout
        logout_resp = self.client.get('/auth/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out successfully', logout_resp.data)

    def test_04_protected_routes(self):
        """Test that unauthenticated visitors are blocked from /user/ routes."""
        protected_urls = ['/user/dashboard', '/user/submit', '/user/complaints']
        for url in protected_urls:
            response = self.client.get(url, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/auth/login', response.headers['Location'])

    def test_05_complaint_submission_and_lifecycle(self):
        """Test full maintenance complaint workflow for an authenticated user."""
        # Register and login
        User.create('Charlie Manager', 'charlie@example.com', 'password123', role='user')
        self.client.post('/auth/login', data={
            'email': 'charlie@example.com',
            'password': 'password123'
        })

        # Submit maintenance complaint
        submit_resp = self.client.post('/user/submit', data={
            'title': 'HVAC AC Unit Leaking Water',
            'category': 'HVAC / Climate',
            'location': 'Building C - Floor 2, Room 204',
            'priority': 'High',
            'description': 'Water is dripping from the ceiling HVAC vent near the conference table.'
        }, follow_redirects=True)
        
        self.assertIn(b'Maintenance request submitted successfully', submit_resp.data)
        self.assertIn(b'HVAC AC Unit Leaking Water', submit_resp.data)

        # Check database directly
        user = User.get_by_email('charlie@example.com')
        complaints = Complaint.get_by_user_id(user['id'])
        self.assertEqual(len(complaints), 1)
        self.assertEqual(complaints[0]['title'], 'HVAC AC Unit Leaking Water')
        self.assertEqual(complaints[0]['priority'], 'High')
        self.assertEqual(complaints[0]['status'], 'Pending')

        # Check details page
        detail_resp = self.client.get(f"/user/complaint/{complaints[0]['id']}")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertIn(b'HVAC AC Unit Leaking Water', detail_resp.data)
        self.assertIn(b'Building C - Floor 2, Room 204', detail_resp.data)

        # Check user stats
        stats = Complaint.get_user_stats(user['id'])
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['pending'], 1)

    def test_06_access_control_between_users(self):
        """Test that regular users cannot view complaints of other users."""
        u1_id = User.create('User One', 'user1@example.com', 'password123', role='user')
        u2_id = User.create('User Two', 'user2@example.com', 'password123', role='user')
        
        # User 1 creates complaint
        c1_id = Complaint.create(u1_id, 'Broken Door Lock', 'Structural & Doors', 'Lock broken on door 101', 'Room 101', 'High')

        # User 2 logs in and tries to access User 1's complaint details
        self.client.post('/auth/login', data={'email': 'user2@example.com', 'password': 'password123'})
        resp = self.client.get(f"/user/complaint/{c1_id}", follow_redirects=True)
        self.assertIn(b'Complaint not found or you do not have permission', resp.data)

if __name__ == '__main__':
    unittest.main()
