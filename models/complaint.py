# models/complaint.py - Complaint / Maintenance Request Model
# -----------------------------------------------------------
# This module manages maintenance requests (complaints/tickets) submitted by users.
#
# Operations:
# - Create a new maintenance request
# - Fetch all requests submitted by a specific user
# - Fetch details for a specific request ID
# - Calculate summary statistics for the user dashboard

from database.db import get_db

class Complaint:
    """
    Model class representing a maintenance complaint/ticket in MaintainX.
    """

    @staticmethod
    def create(user_id, title, category, description, location, priority='Medium'):
        """
        Create a new maintenance complaint record.
        
        Args:
            user_id (int): ID of the authenticated user submitting the request.
            title (str): Brief title of the issue (e.g., 'Broken HVAC in Room 302').
            category (str): Type of maintenance (e.g., 'Electrical', 'Plumbing', 'HVAC').
            description (str): Detailed explanation of the issue.
            location (str): Physical location or room number.
            priority (str): Priority level ('Low', 'Medium', 'High', 'Urgent').
            
        Returns:
            int: The new complaint's ID.
        """
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO complaints (user_id, title, category, description, location, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            """,
            (user_id, title.strip(), category.strip(), description.strip(), location.strip(), priority)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_user_id(user_id, status_filter=None):
        """
        Retrieve all maintenance complaints filed by a given user.
        
        Args:
            user_id (int): ID of the user.
            status_filter (str, optional): Filter by status ('Pending', 'In Progress', 'Resolved').
            
        Returns:
            list[sqlite3.Row]: List of complaint records ordered by newest first.
        """
        db = get_db()
        if status_filter and status_filter != 'All':
            return db.execute(
                """
                SELECT * FROM complaints 
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
                """,
                (user_id, status_filter)
            ).fetchall()
        else:
            return db.execute(
                """
                SELECT * FROM complaints 
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            ).fetchall()

    @staticmethod
    def get_by_id(complaint_id, user_id=None):
        """
        Retrieve a single complaint by ID.
        If user_id is provided, ensures that only the creator (or admin/staff) can view it.
        
        Args:
            complaint_id (int): The primary key ID of the complaint.
            user_id (int, optional): The requesting user's ID for ownership validation.
            
        Returns:
            sqlite3.Row or None: The complaint record or None if not found.
        """
        db = get_db()
        if user_id is not None:
            return db.execute(
                """
                SELECT c.*, u.name as user_name, u.email as user_email
                FROM complaints c
                JOIN users u ON c.user_id = u.id
                WHERE c.id = ? AND c.user_id = ?
                """,
                (complaint_id, user_id)
            ).fetchone()
        else:
            return db.execute(
                """
                SELECT c.*, u.name as user_name, u.email as user_email
                FROM complaints c
                JOIN users u ON c.user_id = u.id
                WHERE c.id = ?
                """,
                (complaint_id,)
            ).fetchone()

    @staticmethod
    def get_user_stats(user_id):
        """
        Compute total, pending, in-progress, and resolved ticket counts for a user.
        
        Args:
            user_id (int): ID of the user.
            
        Returns:
            dict: Dictionary with counts for dashboard metric cards.
        """
        db = get_db()
        rows = db.execute(
            """
            SELECT status, COUNT(*) as count 
            FROM complaints 
            WHERE user_id = ? 
            GROUP BY status
            """,
            (user_id,)
        ).fetchall()
        
        stats = {
            'total': 0,
            'pending': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0
        }
        
        for row in rows:
            status_key = row['status'].lower().replace(' ', '_')
            if status_key in stats:
                stats[status_key] = row['count']
            stats['total'] += row['count']
            
        return stats

    @staticmethod
    def get_recent_by_user(user_id, limit=5):
        """
        Retrieve the most recent maintenance complaints for the dashboard.
        """
        db = get_db()
        return db.execute(
            """
            SELECT * FROM complaints 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
