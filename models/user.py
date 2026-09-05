# models/user.py - User Model & Database Operations
# -----------------------------------------------------------
# This module provides the User model and helper functions for user management,
# registration, password hashing, and authentication.
#
# Key Concepts for Beginners:
# 1. Password Hashing: We NEVER save plain-text passwords. Werkzeug's `generate_password_hash`
#    converts "myPassword123" into a secure cryptographic hash string.
# 2. Parameterized Queries: We use `?` placeholders (e.g. "WHERE email = ?")
#    instead of string formatting. This prevents SQL Injection vulnerabilities.

from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

class User:
    """
    User model class representing an account in MaintainX.
    """
    def __init__(self, id, name, email, password_hash, role='user', created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @staticmethod
    def create(name, email, password, role='user'):
        """
        Create and persist a new user in the database.
        
        Steps:
        1. Hash the user's plain-text password securely.
        2. Insert the record into the 'users' table using get_db().
        3. Commit the transaction to save changes permanently.
        4. Return the newly generated user ID.
        
        Args:
            name (str): User's full name.
            email (str): Unique email address.
            password (str): Plain-text password to hash.
            role (str): Role designation ('user', 'staff', 'admin').
            
        Returns:
            int: The ID of the newly created user record.
        """
        db = get_db()
        
        # Hash the plain-text password using Werkzeug's secure hashing algorithm (pbkdf2:sha256)
        hashed_password = generate_password_hash(password)
        
        # Execute parameterized SQL query
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), hashed_password, role)
        )
        
        # Commit the transaction so data is written to the SQLite file
        db.commit()
        
        return cursor.lastrowid

    @staticmethod
    def get_by_email(email):
        """
        Find a user record by email address.
        
        Args:
            email (str): The email address to look up.
            
        Returns:
            sqlite3.Row or None: User row if found, otherwise None.
        """
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?",
            (email.strip().lower(),)
        ).fetchone()

    @staticmethod
    def get_by_id(user_id):
        """
        Find a user record by their primary key ID.
        
        Args:
            user_id (int): The unique user ID.
            
        Returns:
            sqlite3.Row or None: User row if found, otherwise None.
        """
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    @staticmethod
    def verify_password(stored_hash, password):
        """
        Verify if a plain-text password matches the stored cryptographic hash.
        
        Args:
            stored_hash (str): The hash string stored in the database.
            password (str): The plain-text password entered by the user during login.
            
        Returns:
            bool: True if password is valid, False otherwise.
        """
        return check_password_hash(stored_hash, password)

    @staticmethod
    def get_all():
        """
        Retrieve all registered users (excluding sensitive password hash).
        
        Returns:
            list[sqlite3.Row]: List of user rows.
        """
        db = get_db()
        return db.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
