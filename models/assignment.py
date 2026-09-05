# models/assignment.py - Maintenance Task Assignment Model
# -----------------------------------------------------------
# This module provides models for assigning staff to maintenance complaints.

from database.db import get_db

class Assignment:
    """
    Assignment model connecting a complaint with assigned maintenance staff.
    """
    @staticmethod
    def create(complaint_id, staff_id, notes=None):
        """Assign a staff member to a complaint."""
        db = get_db()
        cursor = db.execute(
            "INSERT INTO assignments (complaint_id, staff_id, notes) VALUES (?, ?, ?)",
            (complaint_id, staff_id, notes)
        )
        # Update complaint status to In Progress
        db.execute(
            "UPDATE complaints SET status = 'In Progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (complaint_id,)
        )
        db.commit()
        return cursor.lastrowid
