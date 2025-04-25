from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection

router = APIRouter(tags=["notifications"])

# Models
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str
    related_to: Optional[str] = None
    related_id: Optional[int] = None
    is_global: bool = False

class NotificationUpdate(BaseModel):
    is_read: bool = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    related_to: Optional[str]
    related_id: Optional[int]
    is_global: bool
    created_at: datetime
    is_read: bool
    read_at: Optional[datetime] = None

# Helper function to create a notification and distribute to users
def create_notification(
    conn, 
    title: str,
    message: str,
    type: str = "info",
    related_to: Optional[str] = None,
    related_id: Optional[int] = None,
    is_global: bool = False,
    created_by: Optional[str] = None,
    target_users: Optional[List[str]] = None
):
    """
    Create a notification and distribute to appropriate users
    
    Args:
        conn: Database connection
        title: Notification title
        message: Notification message
        type: Notification type (info, success, alert)
        related_to: What the notification is related to (e.g., 'schedule')
        related_id: ID of the related entity
        is_global: Whether all users should receive this notification
        created_by: User ID of the creator
        target_users: List of specific user IDs to receive the notification
    """
    try:
        print(f"Creating notification: title='{title}', message='{message}', type='{type}', is_global={is_global}")
        
        # Check if created_by exists in users table, set to NULL if not
        if created_by:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE id = %s", (created_by,))
                user_exists = cursor.fetchone()['count'] > 0
                if not user_exists:
                    print(f"Warning: User with ID '{created_by}' not found. Setting created_by to NULL")
                    created_by = None
        
        with conn.cursor() as cursor:
            # Create the notification
            query = """
            INSERT INTO notifications 
            (title, message, type, related_to, related_id, is_global, created_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """
            cursor.execute(
                query,
                (title, message, type, related_to, related_id, is_global, created_by)
            )
            
            notification_id = cursor.lastrowid
            print(f"Created notification with ID: {notification_id}")
            
            # If global, distribute to all users
            if is_global:
                print("This is a global notification, distributing to all active users")
                cursor.execute("SELECT id FROM users WHERE is_approved = TRUE AND is_active = TRUE")
                users = cursor.fetchall()
                
                if not users:
                    print("Warning: No active users found in the database")
                else:
                    print(f"Distributing notification to {len(users)} users")
                
                for user in users:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO user_notifications (user_id, notification_id, is_read)
                            VALUES (%s, %s, FALSE)
                            """,
                            (user['id'], notification_id)
                        )
                        print(f"Sent notification {notification_id} to user {user['id']}")
                    except Exception as user_error:
                        print(f"Error sending notification to user {user['id']}: {str(user_error)}")
                        # Continue with other users even if one fails
            
            # If target users specified, distribute to them
            elif target_users:
                print(f"Distributing notification to {len(target_users)} specific users")
                for user_id in target_users:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO user_notifications (user_id, notification_id, is_read)
                            VALUES (%s, %s, FALSE)
                            """,
                            (user_id, notification_id)
                        )
                        print(f"Sent notification {notification_id} to user {user_id}")
                    except Exception as user_error:
                        print(f"Error sending notification to user {user_id}: {str(user_error)}")
                        # Continue with other users even if one fails
            else:
                print("Warning: Notification created but not distributed (neither global nor target users specified)")
            
            conn.commit()
            print(f"Notification {notification_id} created and distributed successfully")
            return notification_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating notification: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

# Create a notification when a schedule is approved
def create_schedule_approval_notification(conn, semester_id, created_by=None, schedule_id=None, was_already_current_display_semester=None, is_bulk_approval=False):
    """
    Create a notification when a schedule is approved for a semester
    
    Args:
        conn: Database connection
        semester_id: ID of the semester
        created_by: User ID who approved the schedule
        schedule_id: ID of the schedule being approved (optional)
        was_already_current_display_semester: Boolean flag indicating if this was already the display semester
                                             (passed from the schedule approval route)
        is_bulk_approval: Boolean flag indicating if this is part of a bulk approval process
    """
    try:
        print(f"Creating schedule approval notification: semester_id={semester_id}, created_by={created_by}, schedule_id={schedule_id}, was_already_current_display_semester={was_already_current_display_semester}, is_bulk_approval={is_bulk_approval}")
        with conn.cursor() as cursor:
            # Get semester name
            cursor.execute("SELECT name FROM semesters WHERE id = %s", (semester_id,))
            semester = cursor.fetchone()
            
            if not semester:
                print(f"Semester with ID {semester_id} not found")
                return None
            
            semester_name = semester['name']
            print(f"Found semester name: {semester_name}")
            
            # Check if this semester is the current display semester
            # Use the passed flag if available, otherwise query the database
            is_current_display_semester = False
            
            if was_already_current_display_semester is not None:
                is_current_display_semester = was_already_current_display_semester
                print(f"DEBUG: Using passed flag: was_already_current_display_semester={was_already_current_display_semester}")
            else:
                cursor.execute(
                    "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                )
                setting = cursor.fetchone()
                
                if setting and setting['setting_value'] and str(semester_id) == setting['setting_value']:
                    is_current_display_semester = True
                    print(f"DEBUG: This semester (ID {semester_id}) IS the current display semester (ID {setting['setting_value']})")
                else:
                    print(f"DEBUG: This semester (ID {semester_id}) is NOT the current display semester")
                    if setting:
                        print(f"DEBUG: Current display semester ID is: {setting['setting_value']}")
                    else:
                        print("DEBUG: No current display semester setting found")
            
            # If schedule_id is provided, get details for the specific course
            course_code = None
            section = None
            course_info = ""
            
            if schedule_id:
                cursor.execute(
                    "SELECT course_code, section FROM schedules WHERE id = %s",
                    (schedule_id,)
                )
                schedule_details = cursor.fetchone()
                if schedule_details:
                    course_code = schedule_details['course_code']
                    section = schedule_details['section']
                    course_info = f"{course_code} of {section} in"
                    print(f"Found schedule details: {course_info}")
                else:
                    print(f"Warning: Could not find details for schedule {schedule_id}")
            
            # Check if there are already approved schedules for this semester
            # Exclude the current schedule being approved
            if schedule_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM schedules WHERE semester_id = %s AND status = 'approved' AND id != %s",
                    (semester_id, schedule_id)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM schedules WHERE semester_id = %s AND status = 'approved'",
                    (semester_id,)
                )
            
            approved_count = cursor.fetchone()['count']
            print(f"DEBUG: Found {approved_count} other approved schedules for this semester")
            
            # Print variables for debugging
            print(f"DEBUG: Decision variables: is_current_display_semester={is_current_display_semester}, course_code={course_code}, section={section}, approved_count={approved_count}, is_bulk_approval={is_bulk_approval}")
            
            # For bulk approvals of a new semester, we only want to send "Schedule Posted"
            if is_bulk_approval and not is_current_display_semester:
                print("DEBUG: BULK APPROVAL PATH - Sending only Schedule Posted notification")
                message = f"The schedule for {semester_name} is posted"
                title = "Schedule Posted"
                
                # Check for duplicate "Schedule Posted" notifications for this semester
                cursor.execute(
                    """
                    SELECT id FROM notifications 
                    WHERE title = 'Schedule Posted'
                    AND message = %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
                    LIMIT 1
                    """,
                    (message,)
                )
                existing = cursor.fetchone()
                if existing:
                    print(f"Found existing 'Schedule Posted' notification for {semester_name}. Skipping duplicate.")
                    return existing['id']
            # CASE 1: First schedule in a semester (Schedule Posted)
            elif approved_count == 0:
                print("DEBUG: PATH 1 - First schedule in semester (posted message)")
                message = f"The schedule for {semester_name} is posted"
                title = "Schedule Posted"
                
                # Check for duplicate "Schedule Posted" notifications for this semester
                cursor.execute(
                    """
                    SELECT id FROM notifications 
                    WHERE title = 'Schedule Posted'
                    AND message = %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
                    LIMIT 1
                    """,
                    (message,)
                )
                existing = cursor.fetchone()
                if existing:
                    print(f"Found existing 'Schedule Posted' notification for {semester_name}. Skipping duplicate.")
                    return existing['id']
            
            # CASE 2: Update to a course in the CURRENT display semester 
            elif is_current_display_semester and course_code and section:
                print("DEBUG: PATH 2 - Update message for current display semester")
                # This is an update to a course in the current display semester
                message = f"The schedule for {course_code} of {section} in {semester_name} has been updated"
                title = "Schedule Updated"
                
                # Check for duplicate notifications for this exact course+section (to avoid duplicates for same course)
                cursor.execute(
                    """
                    SELECT id FROM notifications 
                    WHERE title = 'Schedule Updated'
                    AND message = %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 2 MINUTE)
                    LIMIT 1
                    """,
                    (message,)
                )
                existing = cursor.fetchone()
                if existing:
                    print(f"Found existing notification for {course_code} of {section}. Skipping duplicate.")
                    return existing['id']
            
            # CASE 3: Additional course in non-current semester (approved message)
            elif course_code and section and not is_current_display_semester:
                print("DEBUG: PATH 3 - Additional course in non-current semester (approved message)")
                message = f"The schedule for {course_code} of {section} in {semester_name} has been approved"
                title = "Schedule Approved"
                
                # Check for duplicate notifications for this exact course+section
                cursor.execute(
                    """
                    SELECT id FROM notifications 
                    WHERE title = 'Schedule Approved'
                    AND message = %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 2 MINUTE)
                    LIMIT 1
                    """,
                    (message,)
                )
                existing = cursor.fetchone()
                if existing:
                    print(f"Found existing notification for {course_code} of {section}. Skipping duplicate.")
                    return existing['id']
            else:
                print("DEBUG: PATH 4 - No specific course and not first schedule (skipping)")
                # If other schedules are already approved and no specific course, skip notification
                print("Other schedules are already approved and no specific course provided. Skipping notification.")
                return None
            
            print(f"FINAL NOTIFICATION: Creating notification with title: '{title}' and message: '{message}'")
            
            # Create notification
            notification_id = create_notification(
                conn=conn,
                title=title,
                message=message,
                type="success",
                related_to="schedule",
                related_id=semester_id,
                is_global=True,
                created_by=created_by
            )
            
            if notification_id:
                print(f"Successfully created schedule approval notification with ID: {notification_id}")
            else:
                print("Failed to create schedule approval notification")
                
            return notification_id
    except Exception as e:
        print(f"Error creating schedule approval notification: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

# Create a notification when a user's role is changed
def create_role_change_notification(conn, user_id, new_role, created_by=None):
    """
    Create a personalized notification when a user's role is changed
    
    Args:
        conn: Database connection
        user_id: ID of the user whose role was changed
        new_role: The new role assigned to the user
        created_by: User ID who changed the role
    """
    try:
        # Create notification
        return create_notification(
            conn=conn,
            title="Role Updated",
            message=f"Your role has been modified to {new_role}",
            type="info",
            related_to="user",
            related_id=None,
            is_global=False,
            created_by=created_by,
            target_users=[user_id]  # Only send to the specific user
        )
    except Exception as e:
        print(f"Error creating role change notification: {str(e)}")
        return None

# Create a notification when schedules are sent for approval (for the Dean only)
def create_schedule_pending_notification(conn, semester_id, created_by=None, schedule_count=0):
    """
    Create a notification for the Dean when schedules are sent for approval by the Academic Coordinator
    
    Args:
        conn: Database connection
        semester_id: ID of the semester 
        created_by: User ID who sent the schedules for approval
        schedule_count: Number of schedules sent for approval
    """
    try:
        print(f"Creating schedule pending notification: semester_id={semester_id}, created_by={created_by}, schedule_count={schedule_count}")
        with conn.cursor() as cursor:
            # Get semester name
            cursor.execute("SELECT name FROM semesters WHERE id = %s", (semester_id,))
            semester = cursor.fetchone()
            
            if not semester:
                print(f"Semester with ID {semester_id} not found")
                return None
            
            semester_name = semester['name']
            print(f"Found semester name: {semester_name}")
            
            # Find the Dean user ID (the only target for this notification)
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("No Dean user found in the database")
                return None
                
            dean_id = dean_result['id']
            print(f"Found Dean user with ID: {dean_id}")
            
            # Create a count-specific message
            count_text = f"{schedule_count} schedule{'s' if schedule_count != 1 else ''}"
            message = f"{count_text} for {semester_name} pending approval"
            title = "Schedules Pending Approval"
            
            # Check for duplicate notifications within a short time window
            cursor.execute(
                """
                SELECT id FROM notifications 
                WHERE title = 'Schedules Pending Approval'
                AND related_to = 'schedule'
                AND related_id = %s
                AND created_at > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                LIMIT 1
                """,
                (semester_id,)
            )
            existing = cursor.fetchone()
            if existing:
                print(f"Found existing pending approval notification for {semester_name}. Skipping duplicate.")
                return existing['id']
                
            print(f"CREATING NOTIFICATION: title='{title}', message='{message}'")
            
            # Create notification and send only to the Dean
            notification_id = create_notification(
                conn=conn,
                title=title,
                message=message,
                type="alert", # Use alert type to make it more prominent
                related_to="schedule",
                related_id=semester_id,
                is_global=False, # Not global, only for the Dean
                created_by=created_by,
                target_users=[dean_id] # Send only to the Dean
            )
            
            if notification_id:
                print(f"Successfully created schedule pending notification with ID: {notification_id}")
            else:
                print("Failed to create schedule pending notification")
                
            return notification_id
    except Exception as e:
        print(f"Error creating schedule pending notification: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

# Routes
@router.get("/notifications", response_model=List[Dict[str, Any]])
async def get_user_notifications(
    request: Request,
    filter_type: Optional[str] = None,
    sort_by: str = "newest",
    conn = Depends(get_db_connection)
):
    """Get notifications for the current user"""
    try:
        print(f"DEBUG: Received notifications request with filter_type={filter_type}, sort_by={sort_by}")
        print(f"DEBUG: Request headers: {request.headers}")
        print(f"DEBUG: Request query params: {request.query_params}")
        
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
            print(f"DEBUG: Got user_id from query params or headers: {user_id}")
            
            if not user_id:
                print("DEBUG: No user_id found in request")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required"
                )
        else:
            user_id = user_id.id
            print(f"DEBUG: Got user_id from request state: {user_id}")
        
        print(f"DEBUG: Final user_id being used for query: {user_id}")
        
        with conn.cursor() as cursor:
            # First check if the user exists
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE id = %s", (user_id,))
            user_exists = cursor.fetchone()['count'] > 0
            print(f"DEBUG: User exists in database: {user_exists}")
            
            # Check if user has any notifications
            cursor.execute(
                "SELECT COUNT(*) as count FROM user_notifications WHERE user_id = %s",
                (user_id,)
            )
            notification_count = cursor.fetchone()['count']
            print(f"DEBUG: User has {notification_count} notifications in user_notifications table")
            
            # Base query
            query = """
            SELECT n.*, un.is_read, un.read_at
            FROM notifications n
            JOIN user_notifications un ON n.id = un.notification_id
            WHERE un.user_id = %s
            """
            
            params = [user_id]
            
            # Add filter condition if provided
            if filter_type and filter_type != "all":
                query += " AND n.related_to = %s"
                params.append(filter_type)
            
            # Add sorting
            if sort_by == "oldest":
                query += " ORDER BY n.created_at ASC"
            else:
                query += " ORDER BY n.created_at DESC"
            
            print(f"DEBUG: Executing SQL: {query} with params: {params}")
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            print(f"DEBUG: Found {len(notifications)} notifications for user")
            
            # Convert datetime objects to strings for JSON serialization
            for notification in notifications:
                notification['created_at'] = notification['created_at'].isoformat()
                if notification['read_at']:
                    notification['read_at'] = notification['read_at'].isoformat()
            
            return notifications
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching notifications"
        )

@router.get("/dean-notifications", response_model=List[Dict[str, Any]])
async def get_dean_notifications(
    filter_type: Optional[str] = None,
    sort_by: str = "newest",
    conn = Depends(get_db_connection)
):
    """Get notifications for the Dean user, identified directly from the database"""
    try:
        print(f"DEBUG: Received Dean notifications request with filter_type={filter_type}, sort_by={sort_by}")
        
        # Find the Dean user directly from the database
        with conn.cursor() as cursor:
            # Get the Dean user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("DEBUG: No Dean user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Dean user found in the database"
                )
            
            dean_id = dean_result['id']
            print(f"DEBUG: Found Dean user with ID: {dean_id}")
            
            # Check if Dean has any notifications
            cursor.execute(
                "SELECT COUNT(*) as count FROM user_notifications WHERE user_id = %s",
                (dean_id,)
            )
            notification_count = cursor.fetchone()['count']
            print(f"DEBUG: Dean has {notification_count} notifications in user_notifications table")
            
            # Base query
            query = """
            SELECT n.*, un.is_read, un.read_at
            FROM notifications n
            JOIN user_notifications un ON n.id = un.notification_id
            WHERE un.user_id = %s
            """
            
            params = [dean_id]
            
            # Add filter condition if provided
            if filter_type and filter_type != "all":
                query += " AND n.related_to = %s"
                params.append(filter_type)
            
            # Add sorting
            if sort_by == "oldest":
                query += " ORDER BY n.created_at ASC"
            else:
                query += " ORDER BY n.created_at DESC"
            
            print(f"DEBUG: Executing SQL for Dean: {query} with params: {params}")
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            print(f"DEBUG: Found {len(notifications)} notifications for Dean")
            
            # Convert datetime objects to strings for JSON serialization
            for notification in notifications:
                notification['created_at'] = notification['created_at'].isoformat()
                if notification['read_at']:
                    notification['read_at'] = notification['read_at'].isoformat()
            
            return notifications
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching Dean notifications: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Dean notifications: {str(e)}"
        )

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    request: Request,
    conn = Depends(get_db_connection)
):
    """Mark a notification as read"""
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required"
                )
        else:
            user_id = user_id.id
        
        with conn.cursor() as cursor:
            # Check if the notification exists for this user
            cursor.execute(
                """
                SELECT * FROM user_notifications 
                WHERE notification_id = %s AND user_id = %s
                """,
                (notification_id, user_id)
            )
            
            user_notification = cursor.fetchone()
            
            if not user_notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found for this user"
                )
            
            # Mark as read if not already read
            if not user_notification['is_read']:
                cursor.execute(
                    """
                    UPDATE user_notifications 
                    SET is_read = TRUE, read_at = NOW() 
                    WHERE notification_id = %s AND user_id = %s
                    """,
                    (notification_id, user_id)
                )
                
                conn.commit()
            
            return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking notification as read"
        )

@router.patch("/notifications/read-all")
async def mark_all_notifications_as_read(
    request: Request,
    conn = Depends(get_db_connection)
):
    """Mark all notifications as read for a user"""
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required"
                )
        else:
            user_id = user_id.id
        
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE user_notifications 
                SET is_read = TRUE, read_at = NOW() 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (user_id,)
            )
            
            updated_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Marked {updated_count} notifications as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking all notifications as read"
        )

@router.get("/notifications/unread-count")
async def get_unread_notification_count(
    request: Request,
    conn = Depends(get_db_connection)
):
    """Get the count of unread notifications for a user"""
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required"
                )
        else:
            user_id = user_id.id
        
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM user_notifications 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (user_id,)
            )
            
            result = cursor.fetchone()
            return {"count": result['count']}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting unread notification count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting unread notification count"
        )

@router.delete("/notifications/clear-all")
async def clear_all_notifications(
    request: Request,
    conn = Depends(get_db_connection)
):
    """Delete all notifications for a specific user from user_notifications table"""
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required"
                )
        else:
            user_id = user_id.id
        
        with conn.cursor() as cursor:
            # Delete from user_notifications table only (not from notifications table)
            # This ensures that only this user's association with notifications is removed
            cursor.execute(
                """
                DELETE FROM user_notifications 
                WHERE user_id = %s
                """,
                (user_id,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Cleared {deleted_count} notifications for user", "count": deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error clearing notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing notifications"
        )

@router.patch("/dean-notifications/{notification_id}/read")
async def mark_dean_notification_as_read(
    notification_id: int,
    conn = Depends(get_db_connection)
):
    """Mark a notification as read for the Dean user, identified directly from the database"""
    try:
        # Find the Dean user directly from the database
        with conn.cursor() as cursor:
            # Get the Dean user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("DEBUG: No Dean user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Dean user found in the database"
                )
            
            dean_id = dean_result['id']
            print(f"DEBUG: Found Dean user with ID: {dean_id}")
            
            # Check if the notification exists for the Dean
            cursor.execute(
                """
                SELECT * FROM user_notifications 
                WHERE notification_id = %s AND user_id = %s
                """,
                (notification_id, dean_id)
            )
            
            user_notification = cursor.fetchone()
            
            if not user_notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found for Dean"
                )
            
            # Mark as read if not already read
            if not user_notification['is_read']:
                cursor.execute(
                    """
                    UPDATE user_notifications 
                    SET is_read = TRUE, read_at = NOW() 
                    WHERE notification_id = %s AND user_id = %s
                    """,
                    (notification_id, dean_id)
                )
                
                conn.commit()
            
            return {"message": "Dean notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking Dean notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking Dean notification as read"
        )

@router.patch("/dean-notifications/read-all")
async def mark_all_dean_notifications_as_read(
    conn = Depends(get_db_connection)
):
    """Mark all notifications as read for the Dean user, identified directly from the database"""
    try:
        # Find the Dean user directly from the database
        with conn.cursor() as cursor:
            # Get the Dean user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("DEBUG: No Dean user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Dean user found in the database"
                )
            
            dean_id = dean_result['id']
            print(f"DEBUG: Found Dean user with ID: {dean_id}")
            
            cursor.execute(
                """
                UPDATE user_notifications 
                SET is_read = TRUE, read_at = NOW() 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (dean_id,)
            )
            
            updated_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Marked {updated_count} Dean notifications as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking all Dean notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking all Dean notifications as read"
        )

@router.delete("/dean-notifications/clear-all")
async def clear_all_dean_notifications(
    conn = Depends(get_db_connection)
):
    """Delete all notifications for the Dean user, identified directly from the database"""
    try:
        # Find the Dean user directly from the database
        with conn.cursor() as cursor:
            # Get the Dean user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("DEBUG: No Dean user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Dean user found in the database"
                )
            
            dean_id = dean_result['id']
            print(f"DEBUG: Found Dean user with ID: {dean_id}")
            
            # Delete from user_notifications table only (not from notifications table)
            cursor.execute(
                """
                DELETE FROM user_notifications 
                WHERE user_id = %s
                """,
                (dean_id,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Cleared {deleted_count} notifications for Dean", "count": deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error clearing Dean notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing Dean notifications"
        )

@router.get("/acad-coor-notifications", response_model=List[Dict[str, Any]])
async def get_acad_coor_notifications(
    filter_type: Optional[str] = None,
    sort_by: str = "newest",
    conn = Depends(get_db_connection)
):
    """Get notifications for the Academic Coordinator user, identified directly from the database"""
    try:
        print(f"DEBUG: Received Academic Coordinator notifications request with filter_type={filter_type}, sort_by={sort_by}")
        
        # Find the Academic Coordinator user directly from the database
        with conn.cursor() as cursor:
            # Get the Academic Coordinator user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Academic Coordinator' LIMIT 1")
            acad_coor_result = cursor.fetchone()
            
            if not acad_coor_result:
                print("DEBUG: No Academic Coordinator user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Academic Coordinator user found in the database"
                )
            
            acad_coor_id = acad_coor_result['id']
            print(f"DEBUG: Found Academic Coordinator user with ID: {acad_coor_id}")
            
            # Check if Academic Coordinator has any notifications
            cursor.execute(
                "SELECT COUNT(*) as count FROM user_notifications WHERE user_id = %s",
                (acad_coor_id,)
            )
            notification_count = cursor.fetchone()['count']
            print(f"DEBUG: Academic Coordinator has {notification_count} notifications in user_notifications table")
            
            # Base query
            query = """
            SELECT n.*, un.is_read, un.read_at
            FROM notifications n
            JOIN user_notifications un ON n.id = un.notification_id
            WHERE un.user_id = %s
            """
            
            params = [acad_coor_id]
            
            # Add filter condition if provided
            if filter_type and filter_type != "all":
                query += " AND n.related_to = %s"
                params.append(filter_type)
            
            # Add sorting
            if sort_by == "oldest":
                query += " ORDER BY n.created_at ASC"
            else:
                query += " ORDER BY n.created_at DESC"
            
            print(f"DEBUG: Executing SQL for Academic Coordinator: {query} with params: {params}")
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            print(f"DEBUG: Found {len(notifications)} notifications for Academic Coordinator")
            
            # Convert datetime objects to strings for JSON serialization
            for notification in notifications:
                notification['created_at'] = notification['created_at'].isoformat()
                if notification['read_at']:
                    notification['read_at'] = notification['read_at'].isoformat()
            
            return notifications
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching Academic Coordinator notifications: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Academic Coordinator notifications: {str(e)}"
        )

@router.patch("/acad-coor-notifications/{notification_id}/read")
async def mark_acad_coor_notification_as_read(
    notification_id: int,
    conn = Depends(get_db_connection)
):
    """Mark a notification as read for the Academic Coordinator user, identified directly from the database"""
    try:
        # Find the Academic Coordinator user directly from the database
        with conn.cursor() as cursor:
            # Get the Academic Coordinator user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Academic Coordinator' LIMIT 1")
            acad_coor_result = cursor.fetchone()
            
            if not acad_coor_result:
                print("DEBUG: No Academic Coordinator user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Academic Coordinator user found in the database"
                )
            
            acad_coor_id = acad_coor_result['id']
            print(f"DEBUG: Found Academic Coordinator user with ID: {acad_coor_id}")
            
            # Check if the notification exists for the Academic Coordinator
            cursor.execute(
                """
                SELECT * FROM user_notifications 
                WHERE notification_id = %s AND user_id = %s
                """,
                (notification_id, acad_coor_id)
            )
            
            user_notification = cursor.fetchone()
            
            if not user_notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found for Academic Coordinator"
                )
            
            # Mark as read if not already read
            if not user_notification['is_read']:
                cursor.execute(
                    """
                    UPDATE user_notifications 
                    SET is_read = TRUE, read_at = NOW() 
                    WHERE notification_id = %s AND user_id = %s
                    """,
                    (notification_id, acad_coor_id)
                )
                
                conn.commit()
            
            return {"message": "Academic Coordinator notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking Academic Coordinator notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking Academic Coordinator notification as read"
        )

@router.patch("/acad-coor-notifications/read-all")
async def mark_all_acad_coor_notifications_as_read(
    conn = Depends(get_db_connection)
):
    """Mark all notifications as read for the Academic Coordinator user, identified directly from the database"""
    try:
        # Find the Academic Coordinator user directly from the database
        with conn.cursor() as cursor:
            # Get the Academic Coordinator user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Academic Coordinator' LIMIT 1")
            acad_coor_result = cursor.fetchone()
            
            if not acad_coor_result:
                print("DEBUG: No Academic Coordinator user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Academic Coordinator user found in the database"
                )
            
            acad_coor_id = acad_coor_result['id']
            print(f"DEBUG: Found Academic Coordinator user with ID: {acad_coor_id}")
            
            cursor.execute(
                """
                UPDATE user_notifications 
                SET is_read = TRUE, read_at = NOW() 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (acad_coor_id,)
            )
            
            updated_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Marked {updated_count} Academic Coordinator notifications as read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error marking all Academic Coordinator notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking all Academic Coordinator notifications as read"
        )

@router.delete("/acad-coor-notifications/clear-all")
async def clear_all_acad_coor_notifications(
    conn = Depends(get_db_connection)
):
    """Delete all notifications for the Academic Coordinator user, identified directly from the database"""
    try:
        # Find the Academic Coordinator user directly from the database
        with conn.cursor() as cursor:
            # Get the Academic Coordinator user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Academic Coordinator' LIMIT 1")
            acad_coor_result = cursor.fetchone()
            
            if not acad_coor_result:
                print("DEBUG: No Academic Coordinator user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Academic Coordinator user found in the database"
                )
            
            acad_coor_id = acad_coor_result['id']
            print(f"DEBUG: Found Academic Coordinator user with ID: {acad_coor_id}")
            
            # Delete from user_notifications table only (not from notifications table)
            cursor.execute(
                """
                DELETE FROM user_notifications 
                WHERE user_id = %s
                """,
                (acad_coor_id,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {"message": f"Cleared {deleted_count} notifications for Academic Coordinator", "count": deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error clearing Academic Coordinator notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing Academic Coordinator notifications"
        )

@router.get("/dean-notifications/unread-count")
async def get_dean_unread_notification_count(
    conn = Depends(get_db_connection)
):
    """Get the count of unread notifications for the Dean user, identified directly from the database"""
    try:
        # Find the Dean user directly from the database
        with conn.cursor() as cursor:
            # Get the Dean user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Dean' LIMIT 1")
            dean_result = cursor.fetchone()
            
            if not dean_result:
                print("DEBUG: No Dean user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Dean user found in the database"
                )
            
            dean_id = dean_result['id']
            print(f"DEBUG: Found Dean user with ID: {dean_id}")
            
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM user_notifications 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (dean_id,)
            )
            
            result = cursor.fetchone()
            print(f"DEBUG: Dean has {result['count']} unread notifications")
            return {"count": result['count']}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting Dean unread notification count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting Dean unread notification count"
        )

@router.get("/acad-coor-notifications/unread-count")
async def get_acad_coor_unread_notification_count(
    conn = Depends(get_db_connection)
):
    """Get the count of unread notifications for the Academic Coordinator user, identified directly from the database"""
    try:
        # Find the Academic Coordinator user directly from the database
        with conn.cursor() as cursor:
            # Get the Academic Coordinator user ID from the database
            cursor.execute("SELECT id FROM users WHERE role = 'Academic Coordinator' LIMIT 1")
            acad_coor_result = cursor.fetchone()
            
            if not acad_coor_result:
                print("DEBUG: No Academic Coordinator user found in the database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Academic Coordinator user found in the database"
                )
            
            acad_coor_id = acad_coor_result['id']
            print(f"DEBUG: Found Academic Coordinator user with ID: {acad_coor_id}")
            
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM user_notifications 
                WHERE user_id = %s AND is_read = FALSE
                """,
                (acad_coor_id,)
            )
            
            result = cursor.fetchone()
            print(f"DEBUG: Academic Coordinator has {result['count']} unread notifications")
            return {"count": result['count']}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting Academic Coordinator unread notification count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting Academic Coordinator unread notification count"
        ) 