# models/staff.py - Staff Model
# -----------------------------------------------------------
# This module provides models and helpers for maintenance staff members.

from database.db import get_db

class Staff:
    """
    Staff model representing maintenance personnel in the facility.
    """
    @staticmethod
    def get_all():
        """Retrieve all staff members with user information."""
        db = get_db()
        return db.execute(
            """
            SELECT s.*, u.name, u.email 
            FROM staff s
            JOIN users u ON s.user_id = u.id
            ORDER BY u.name ASC
            """
        ).fetchall()

    @staticmethod
    def get_by_user_id(user_id):
        """Find staff record associated with a user ID."""
        db = get_db()
        return db.execute(
            "SELECT * FROM staff WHERE user_id = ?",
            (user_id,)
        ).fetchone()
