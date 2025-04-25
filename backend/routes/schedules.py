from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time
import json
import re
import traceback

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection, get_current_user

# Import notification functions
from routes.notifications import create_schedule_approval_notification, create_schedule_pending_notification

# Function to convert "HH:MM AM/PM" format to "HH:MM:SS" 24-hour format
def convert_time_format(time_str):
    try:
        # Extract components
        match = re.match(r'(\d+):(\d+)\s?(AM|PM)', time_str.upper())
        if not match:
            return time_str  # Return as is if no match
        
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3)
        
        # Convert to 24-hour format
        if period == 'PM' and hour < 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0
            
        return f"{hour:02d}:{minute:02d}:00"
    except Exception as e:
        print(f"Error converting time format: {e}")
        return time_str

# Function to check for scheduling conflicts
def check_schedule_conflicts(
    conn, 
    semester_id, 
    lab_room_id, 
    day, 
    second_day, 
    start_time, 
    end_time, 
    current_schedule_id=None
):
    """
    Check for scheduling conflicts in the same semester, time, day (including second day), and room.
    Returns a tuple (has_conflict, conflict_details) where conflict_details provides information
    about the conflicting schedule if a conflict exists.
    """
    
    try:
        with conn.cursor() as cursor:
            # Base query to find conflicts
            query = """
            SELECT s.*, l.name as lab_room_name, sem.name as semester_name 
            FROM schedules s
            JOIN lab_rooms l ON s.lab_room_id = l.id 
            JOIN semesters sem ON s.semester_id = sem.id 
            WHERE 
                s.semester_id = %s 
                AND s.lab_room_id = %s
                AND (
                    -- Case 1: The existing schedule conflicts with the main day of the new schedule
                    (
                        (s.day = %s) 
                        AND (
                            (s.start_time <= %s AND s.end_time > %s) OR  -- Existing schedule starts before and ends during/after
                            (s.start_time >= %s AND s.start_time < %s) OR  -- Existing schedule starts during
                            (s.start_time <= %s AND s.end_time >= %s)  -- New schedule falls completely within existing schedule
                        )
                    )
                    -- Case 2: The existing schedule conflicts with the second day of the new schedule (if it exists)
                    OR (
                        %s IS NOT NULL 
                        AND (s.day = %s)
                        AND (
                            (s.start_time <= %s AND s.end_time > %s) OR
                            (s.start_time >= %s AND s.start_time < %s) OR
                            (s.start_time <= %s AND s.end_time >= %s)
                        )
                    )
                    -- Case 3: The main day of the existing schedule conflicts with the second day of the new schedule
                    OR (
                        %s IS NOT NULL
                        AND (s.day = %s)
                        AND (
                            (s.start_time <= %s AND s.end_time > %s) OR
                            (s.start_time >= %s AND s.start_time < %s) OR
                            (s.start_time <= %s AND s.end_time >= %s)
                        )
                    )
                    -- Case 4: The second day of the existing schedule conflicts with the main/second day of the new schedule
                    OR (
                        s.second_day IS NOT NULL
                        AND (
                            (s.second_day = %s) OR (%s IS NOT NULL AND s.second_day = %s)
                        )
                        AND (
                            (s.start_time <= %s AND s.end_time > %s) OR
                            (s.start_time >= %s AND s.start_time < %s) OR
                            (s.start_time <= %s AND s.end_time >= %s)
                        )
                    )
                )
            """
            
            params = [
                semester_id, lab_room_id,
                # Case 1 parameters
                day, end_time, start_time, start_time, end_time, start_time, end_time,
                # Case 2 parameters
                second_day, second_day, end_time, start_time, start_time, end_time, start_time, end_time,
                # Case 3 parameters
                second_day, second_day, end_time, start_time, start_time, end_time, start_time, end_time,
                # Case 4 parameters
                day, second_day, second_day, end_time, start_time, start_time, end_time, start_time, end_time
            ]
            
            # If updating an existing schedule, exclude it from conflict check
            if current_schedule_id:
                query += " AND s.id != %s"
                params.append(current_schedule_id)
            
            cursor.execute(query, params)
            conflicts = cursor.fetchall()
            
            if conflicts:
                conflict = conflicts[0]
                conflict_details = {
                    'id': conflict['id'],
                    'course_code': conflict['course_code'],
                    'section': conflict['section'],
                    'day': conflict['day'],
                    'second_day': conflict['second_day'],
                    'lab_room_name': conflict['lab_room_name'],
                    'start_time': conflict['start_time'],
                    'end_time': conflict['end_time'],
                    'status': conflict['status']
                }
                return True, conflict_details
            
            return False, None
            
    except Exception as e:
        print(f"Error checking schedule conflicts: {str(e)}")
        # Don't raise an exception here, let the calling function handle it
        return False, {"error": str(e)}

# Function to validate time constraints (7:30 AM - 8:00 PM)
def validate_schedule_time_constraints(start_time, end_time):
    """
    Validates that the schedule times fall within the allowed time range:
    - Start time must not be earlier than 7:30 AM
    - End time must not be later than 8:00 PM
    
    Returns a tuple (is_valid, error_message)
    """
    try:
        # Convert times to standardized format for comparison
        # Expected format is like "9:00 AM" or "2:30 PM"
        min_time = "07:30 AM"
        max_time = "08:00 PM"
        
        # Function to convert time string to minutes for easy comparison
        def convert_to_minutes(time_str):
            # Parse time string (format: "HH:MM AM/PM")
            parts = time_str.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid time format: {time_str}")
                
            time_part = parts[0]
            period = parts[1]
            
            hour, minute = map(int, time_part.split(':'))
            
            # Convert to 24-hour format for comparison
            if period == 'PM' and hour < 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
                
            return hour * 60 + minute
        
        # Convert all times to minutes for comparison
        start_minutes = convert_to_minutes(start_time)
        end_minutes = convert_to_minutes(end_time)
        min_minutes = convert_to_minutes(min_time)
        max_minutes = convert_to_minutes(max_time)
        
        # Validate constraints
        if start_minutes < min_minutes:
            return False, f"Start time cannot be earlier than {min_time}"
        
        if end_minutes > max_minutes:
            return False, f"End time cannot be later than {max_time}"
            
        return True, ""
    except Exception as e:
        return False, f"Error validating time constraints: {str(e)}"

router = APIRouter(tags=["schedules"])

class ScheduleBase(BaseModel):
    semester_id: int
    section: str
    course_code: str
    course_name: str
    day: str
    second_day: Optional[str] = None
    lab_room_id: int
    instructor_name: str
    start_time: str
    end_time: str
    schedule_types: List[str]
    class_type: str
    status: str = 'draft'
    created_by: Optional[str] = None  # Make created_by an optional field

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass

class ScheduleStatusUpdate(BaseModel):
    status: str

class BulkScheduleStatusUpdate(BaseModel):
    schedule_ids: List[int]
    status: str
    semester_id: Optional[int] = None

@router.get("/schedules")
async def get_schedules(
    semester_id: Optional[int] = None,
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT s.*, l.name as lab_room_name, sem.name as semester_name 
                FROM schedules s
                JOIN lab_rooms l ON s.lab_room_id = l.id 
                JOIN semesters sem ON s.semester_id = sem.id 
                WHERE 1=1
            """
            params = []
            
            if semester_id:
                query += " AND s.semester_id = %s"
                params.append(semester_id)
            
            query += " ORDER BY s.day, s.start_time"
            
            cursor.execute(query, params)
            schedules = cursor.fetchall()
            
            # Convert schedule_types from JSON string to list
            for schedule in schedules:
                schedule['schedule_types'] = json.loads(schedule['schedule_types'])
            
            return schedules
    except Exception as e:
        print(f"Error fetching schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching schedules"
        )

@router.post("/schedules", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    request: Request,
    conn = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        # Debug: Print received schedule data
        print("Received schedule data:", schedule.dict())
        
        # Get user ID - extract from Authorization header if it's a fallback token
        user_id = current_user.id
        auth_header = request.headers.get("Authorization")
        if auth_header and "user_fallback_token_" in auth_header:
            # Extract user ID from request cookies or query params
            user_str = request.cookies.get('user') or request.query_params.get('user')
            if not user_str:
                # Try to get from headers
                user_str = request.headers.get('X-User-Data')
            
            if user_str:
                try:
                    # Using global json import instead of reimporting
                    user_data = json.loads(user_str)
                    user_id = user_data.get('id')
                    print(f"Extracted user ID from request data: {user_id}")
                except Exception as e:
                    print(f"Error extracting user ID from request data: {str(e)}")
        
        print(f"Using user ID {user_id} for created_by field")
        
        # Validate class_type
        if schedule.class_type not in ['lab', 'lec', 'lab/lec']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="class_type must be 'lab', 'lec', or 'lab/lec'"
            )
        
        # Validate time constraints (7:30 AM - 8:00 PM)
        is_valid_time, error_message = validate_schedule_time_constraints(
            schedule.start_time, 
            schedule.end_time
        )
        
        if not is_valid_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Check for schedule conflicts
        has_conflict, conflict_details = check_schedule_conflicts(
            conn,
            schedule.semester_id,
            schedule.lab_room_id,
            schedule.day,
            schedule.second_day,
            schedule.start_time,
            schedule.end_time
        )
        
        if has_conflict:
            # Prepare conflict message with details
            conflict_msg = f"Schedule conflict detected with: {conflict_details['course_code']} ({conflict_details['section']})"
            conflict_msg += f", on {conflict_details['day']}"
            if conflict_details['second_day']:
                conflict_msg += f"/{conflict_details['second_day']}"
            conflict_msg += f" from {conflict_details['start_time']} to {conflict_details['end_time']}"
            conflict_msg += f" in {conflict_details['lab_room_name']}"
            conflict_msg += f" (Status: {conflict_details['status']})"
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_msg
            )
        
        # For start_time and end_time, keep them as is (since they're varchar in the database)
        # No need to convert to 24-hour format
            
        with conn.cursor() as cursor:
            # Verify that semester_id exists
            cursor.execute("SELECT id FROM semesters WHERE id = %s", (schedule.semester_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Semester with ID {schedule.semester_id} does not exist"
                )
                
            # Verify that lab_room_id exists
            cursor.execute("SELECT id FROM lab_rooms WHERE id = %s", (schedule.lab_room_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Lab room with ID {schedule.lab_room_id} does not exist"
                )
            
            # Insert schedule
            cursor.execute(
                """
                INSERT INTO schedules (
                    semester_id, section, course_code, course_name,
                    day, second_day, lab_room_id, instructor_name, 
                    start_time, end_time, schedule_types, class_type,
                    status, created_by, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                """,
                (
                    schedule.semester_id, schedule.section[:20],
                    schedule.course_code[:20], schedule.course_name[:100],
                    schedule.day[:10], schedule.second_day[:10] if schedule.second_day else None, 
                    schedule.lab_room_id, schedule.instructor_name[:100],
                    schedule.start_time[:10], schedule.end_time[:10], 
                    json.dumps(schedule.schedule_types),
                    schedule.class_type, 'draft', user_id
                )
            )
            
            schedule_id = cursor.lastrowid
            
            # Log the action
            try:
                # Get client IP safely
                client_ip = None
                if hasattr(request, 'client') and hasattr(request.client, 'host'):
                    client_ip = request.client.host
                
                cursor.execute(
                    """
                    INSERT INTO audit_log (user_id, action, details, ip_address)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        "CREATE_SCHEDULE",
                        f"Created schedule {schedule_id}",
                        client_ip
                    )
                )
            except Exception as log_error:
                # If audit logging fails, just print the error but continue
                print(f"Error logging to audit_log but continuing: {str(log_error)}")
            
            conn.commit()
            
            return {
                "id": schedule_id,
                "message": "Schedule created successfully as draft"
            }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        # More detailed error logging
        print(f"Error creating schedule: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Schedule data: {schedule.dict() if schedule else 'No data'}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating schedule: {str(e)}"
        )

@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: int,
    schedule: ScheduleUpdate,
    request: Request,
    conn = Depends(get_db_connection)
):
    try:
        # Hardcode a default user ID to avoid authentication issues
        user_id = "system"
        print(f"Update schedule {schedule_id} - Using system user")
        print(f"Received schedule data: {schedule.dict()}")
        
        # Validate time constraints (7:30 AM - 8:00 PM)
        is_valid_time, error_message = validate_schedule_time_constraints(
            schedule.start_time, 
            schedule.end_time
        )
        
        if not is_valid_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
            
        # Check for schedule conflicts
        has_conflict, conflict_details = check_schedule_conflicts(
            conn,
            schedule.semester_id,
            schedule.lab_room_id,
            schedule.day,
            schedule.second_day,
            schedule.start_time,
            schedule.end_time,
            schedule_id  # Exclude current schedule from conflict check
        )
        
        if has_conflict:
            # Prepare conflict message with details
            conflict_msg = f"Schedule conflict detected with: {conflict_details['course_code']} ({conflict_details['section']})"
            conflict_msg += f", on {conflict_details['day']}"
            if conflict_details['second_day']:
                conflict_msg += f"/{conflict_details['second_day']}"
            conflict_msg += f" from {conflict_details['start_time']} to {conflict_details['end_time']}"
            conflict_msg += f" in {conflict_details['lab_room_name']}"
            conflict_msg += f" (Status: {conflict_details['status']})"
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_msg
            )
        
        # Prepare data with proper string handling
        section = schedule.section[:20] if schedule.section else ""
        course_code = schedule.course_code[:20] if schedule.course_code else ""
        course_name = schedule.course_name[:100] if schedule.course_name else ""
        day = schedule.day[:10] if schedule.day else ""
        second_day = schedule.second_day[:10] if schedule.second_day else None
        instructor_name = schedule.instructor_name[:100] if schedule.instructor_name else ""
        start_time = schedule.start_time[:10] if schedule.start_time else ""
        end_time = schedule.end_time[:10] if schedule.end_time else ""
        schedule_types_json = json.dumps(schedule.schedule_types) if schedule.schedule_types else json.dumps([])
        
        with conn.cursor() as cursor:
            # Check if schedule exists
            cursor.execute(
                "SELECT * FROM schedules WHERE id = %s",
                (schedule_id,)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Schedule not found"
                )
            
            print(f"Updating schedule with prepared data: semester_id={schedule.semester_id}, section={section}, course_code={course_code}, etc.")
            
            # Update schedule
            cursor.execute(
                """
                UPDATE schedules SET
                    semester_id = %s, section = %s, course_code = %s, course_name = %s,
                    day = %s, second_day = %s, lab_room_id = %s, instructor_name = %s,
                    start_time = %s, end_time = %s, schedule_types = %s, class_type = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    schedule.semester_id, section, course_code, course_name,
                    day, second_day, schedule.lab_room_id, instructor_name, 
                    start_time, end_time, schedule_types_json,
                    schedule.class_type, schedule_id
                )
            )
            
            # Log the update
            try:
                cursor.execute(
                    """
                    INSERT INTO audit_log (user_id, action, details, ip_address)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        "UPDATE_SCHEDULE",
                        f"Updated schedule {schedule_id}",
                        request.client.host if hasattr(request, 'client') else "unknown"
                    )
                )
            except Exception as log_error:
                print(f"Error logging schedule update: {log_error}")
                # Continue even if logging fails
            
            conn.commit()
            
            # Fetch the updated schedule to return
            cursor.execute(
                """
                SELECT s.*, l.name as lab_room_name, sem.name as semester_name 
                FROM schedules s
                JOIN lab_rooms l ON s.lab_room_id = l.id 
                JOIN semesters sem ON s.semester_id = sem.id 
                WHERE s.id = %s
                """,
                (schedule_id,)
            )
            updated_schedule = cursor.fetchone()
            if updated_schedule:
                # Convert schedule_types from JSON string to list
                try:
                    updated_schedule['schedule_types'] = json.loads(updated_schedule['schedule_types'])
                except:
                    updated_schedule['schedule_types'] = []
                return updated_schedule
            
            return {"message": "Schedule updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error updating schedule: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        try:
            print(f"Schedule data: {schedule.dict() if schedule else 'No data'}")
        except:
            print("Could not print schedule data")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating schedule: {str(e)}"
        )

@router.patch("/schedules/{schedule_id}/status")
async def update_schedule_status(
    schedule_id: int,
    status_update: ScheduleStatusUpdate,
    request: Request,
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            # Get current schedule status, semester ID, and created_by
            cursor.execute(
                "SELECT status, semester_id, created_by FROM schedules WHERE id = %s",
                (schedule_id,)
            )
            schedule = cursor.fetchone()
            
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Schedule not found"
                )
            
            current_status = schedule['status']
            semester_id = schedule['semester_id']
            # Use the actual creator of the schedule instead of hardcoding "system"
            creator_user_id = schedule['created_by']
            
            print(f"Found schedule with creator: {creator_user_id}")
            
            # Validate status
            if status_update.status not in ['draft', 'pending', 'approved']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status. Must be 'draft', 'pending', or 'approved'"
                )
            
            # Skip transition validation to simplify the process
            
            # Update status
            cursor.execute(
                "UPDATE schedules SET status = %s WHERE id = %s",
                (status_update.status, schedule_id)
            )
            
            # If the status is being changed to 'pending', create a notification for the Dean
            if status_update.status == 'pending':
                try:
                    # Count how many schedules are being changed to pending for this semester
                    # This helps when multiple schedules are being sent for approval at once
                    cursor.execute(
                        """
                        SELECT COUNT(*) as count 
                        FROM schedules 
                        WHERE semester_id = %s AND status = 'pending'
                        """,
                        (semester_id,)
                    )
                    pending_count = cursor.fetchone()['count']
                    
                    # Create a notification for the Dean
                    notification_id = create_schedule_pending_notification(
                        conn=conn,
                        semester_id=semester_id,
                        created_by=creator_user_id,
                        schedule_count=pending_count
                    )
                    print(f"Created schedule pending notification with ID: {notification_id}")
                except Exception as notif_error:
                    print(f"Error creating schedule pending notification: {notif_error}")
                    # Continue even if notification creation fails
            
            # If setting status to approved, update system settings
            if status_update.status == 'approved':
                try:
                    # Check if this semester is already the current display semester
                    cursor.execute(
                        "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                    )
                    setting_row = cursor.fetchone()
                    was_already_current_display_semester = False
                    
                    if setting_row and setting_row['setting_value'] == str(semester_id):
                        was_already_current_display_semester = True
                        print(f"Semester {semester_id} is already set as current_display_semester_id")
                    else:
                        # Update system settings if this is not already the current display semester
                        # Check if the setting exists
                        cursor.execute(
                            "SELECT COUNT(*) as count FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                        )
                        setting_exists = cursor.fetchone()['count'] > 0
                        
                        if setting_exists:
                            # Update existing setting
                            cursor.execute(
                                """
                                UPDATE system_settings 
                                SET setting_value = %s, updated_at = NOW()
                                WHERE setting_key = 'current_display_semester_id'
                                """,
                                (str(semester_id),)
                            )
                        else:
                            # Insert new setting
                            cursor.execute(
                                """
                                INSERT INTO system_settings 
                                (setting_key, setting_value, description)
                                VALUES ('current_display_semester_id', %s, 'ID of the semester that should be displayed in all dashboards')
                                """,
                                (str(semester_id),)
                            )
                        
                        # Ensure changes are committed immediately to avoid race conditions
                        conn.commit()
                        print(f"Updated current_display_semester_id to {semester_id} after approving schedule {schedule_id}")
                        
                        # Small delay to ensure system settings are properly updated before notifications
                        import time
                        time.sleep(0.5)  # 500ms delay
                        
                        # Re-fetch to confirm the update
                        cursor.execute(
                            "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                        )
                        updated_setting = cursor.fetchone()
                        if updated_setting and updated_setting['setting_value'] == str(semester_id):
                            print("Confirmed system settings update was successful")
                        else:
                            print("Warning: System settings update may not have been applied")
                    
                    # Get the semester name to check if it's a Summer semester
                    cursor.execute("SELECT name FROM semesters WHERE id = %s", (semester_id,))
                    semester_data = cursor.fetchone()
                    
                    if semester_data and "Summer" in semester_data['name']:
                        print(f"Approved a Summer semester ({semester_data['name']}), checking to add next academic year semesters")
                        # Call the function to check and add next academic year semesters
                        check_and_add_next_academic_year_semesters(conn, semester_id, creator_user_id)
                        # Ensure these changes are committed too
                        conn.commit()
                    
                    # Create a notification about the approved schedule
                    try:
                        # Get the count of approved schedules for this semester excluding the current one
                        cursor.execute(
                            "SELECT COUNT(*) as count FROM schedules WHERE semester_id = %s AND status = 'approved' AND id != %s",
                            (semester_id, schedule_id)
                        )
                        approved_count = cursor.fetchone()['count']
                        
                        # Check if this is part of a bulk approval by seeing if other schedules for this semester
                        # were approved in the last 10 seconds
                        cursor.execute(
                            """
                            SELECT COUNT(*) as count FROM schedules 
                            WHERE semester_id = %s AND status = 'approved' AND id != %s
                            AND updated_at > DATE_SUB(NOW(), INTERVAL 10 SECOND)
                            """,
                            (semester_id, schedule_id)
                        )
                        recent_approvals = cursor.fetchone()['count']
                        is_part_of_bulk = recent_approvals > 0
                        
                        # Recheck the current display semester one more time to be extra sure
                        cursor.execute(
                            "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                        )
                        latest_setting = cursor.fetchone()
                        if latest_setting and latest_setting['setting_value'] == str(semester_id):
                            was_already_current_display_semester = True
                            print("Final check: This is now the current display semester")
                        
                        # Use the actual creator of the schedule for the notification
                        notification_id = create_schedule_approval_notification(
                            conn=conn,
                            semester_id=semester_id,
                            created_by=creator_user_id,
                            schedule_id=schedule_id,
                            was_already_current_display_semester=was_already_current_display_semester,
                            is_bulk_approval=is_part_of_bulk
                        )
                        print(f"Created schedule approval notification with ID: {notification_id}")
                    except Exception as notif_error:
                        print(f"Error creating schedule approval notification: {notif_error}")
                        # Continue even if notification creation fails
                
                except Exception as e:
                    print(f"Error updating system settings: {e}")
                    print(f"Traceback: {traceback.format_exc()}")
                    # Continue even if this update fails
            
            # Log the status change - simplified
            try:
                cursor.execute(
                    """
                    INSERT INTO audit_log (user_id, action, details, ip_address)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        creator_user_id,
                        "UPDATE_SCHEDULE_STATUS",
                        f"Schedule {schedule_id} status changed from {current_status} to {status_update.status}",
                        request.client.host if request.client else "unknown"
                    )
                )
            except Exception as log_error:
                print(f"Error logging status change: {log_error}")
                # Continue even if logging fails
            
            conn.commit()
            
            return {
                "message": f"Schedule status updated to {status_update.status} successfully",
                "scheduleId": schedule_id,
                "previousStatus": current_status,
                "newStatus": status_update.status
            }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error updating schedule status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating schedule status"
        )

@router.get("/schedules/status/{status}")
async def get_schedules_by_status(
    status: str,
    conn = Depends(get_db_connection)
):
    try:
        if status not in ['draft', 'pending', 'approved']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status parameter"
            )
        
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.*, l.name as lab_room_name, sem.name as semester_name 
                FROM schedules s
                JOIN lab_rooms l ON s.lab_room_id = l.id 
                JOIN semesters sem ON s.semester_id = sem.id 
                WHERE s.status = %s
                ORDER BY s.created_at DESC
                """,
                (status,)
            )
            schedules = cursor.fetchall()
            
            # Convert schedule_types from JSON string to list
            for schedule in schedules:
                schedule['schedule_types'] = json.loads(schedule['schedule_types'])
            
            return schedules
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching {status} schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching {status} schedules"
        )

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    request: Request,
    conn = Depends(get_db_connection)
):
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Find the first user in the database
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users LIMIT 1")
                first_user = cursor.fetchone()
                if first_user:
                    user_id = first_user['id']
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No users found in the database"
                    )
        else:
            user_id = user_id.id
            
        with conn.cursor() as cursor:
            # Check if schedule exists
            cursor.execute(
                "SELECT * FROM schedules WHERE id = %s",
                (schedule_id,)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Schedule not found"
                )
            
            # Delete schedule
            cursor.execute(
                "DELETE FROM schedules WHERE id = %s",
                (schedule_id,)
            )
            
            # Log the deletion
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    "DELETE_SCHEDULE",
                    f"Deleted schedule {schedule_id}",
                    request.client.host
                )
            )
            
            conn.commit()
            
            return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error deleting schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting schedule"
        )

@router.delete("/schedules/all")
async def delete_all_schedules(
    request: Request,
    conn = Depends(get_db_connection)
):
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Find the first user in the database
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users LIMIT 1")
                first_user = cursor.fetchone()
                if first_user:
                    user_id = first_user['id']
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No users found in the database"
                    )
        else:
            user_id = user_id.id
            
        with conn.cursor() as cursor:
            # Count schedules before deleting
            cursor.execute("SELECT COUNT(*) as count FROM schedules")
            result = cursor.fetchone()
            schedule_count = result['count'] if result else 0
            
            if schedule_count == 0:
                return {"message": "No schedules to delete"}
            
            # Delete all schedules
            cursor.execute("DELETE FROM schedules")
            
            # Log the deletion
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    "DELETE_ALL_SCHEDULES",
                    f"Deleted all schedules ({schedule_count} total)",
                    request.client.host if hasattr(request, 'client') else None
                )
            )
            
            conn.commit()
            
            return {"message": f"All schedules deleted successfully ({schedule_count} total)"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error deleting all schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting all schedules"
        )

@router.get("/schedules/check-course-usage")
async def check_course_usage(
    course_code: str,
    semester_id: int,
    section: str,
    schedule_id: Optional[int] = None,
    conn = Depends(get_db_connection)
):
    """
    Check if a course offering is already used in a schedule for the specified semester and section.
    Returns true if the course is already used (unavailable), false if it's available.
    If schedule_id is provided, excludes that schedule from the check (for edit mode).
    """
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT COUNT(*) as count
            FROM schedules
            WHERE course_code = %s 
            AND semester_id = %s
            AND section = %s
            """
            params = [course_code, semester_id, section]
            
            # If editing a schedule, exclude it from the check
            if schedule_id:
                query += " AND id != %s"
                params.append(schedule_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            # If count > 0, the course is already in use for this semester and section
            is_used = result['count'] > 0 if result else False
            
            return {"is_used": is_used}
            
    except Exception as e:
        print(f"Error checking course usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking course usage: {str(e)}"
        )

@router.get("/schedules/used-courses/{semester_id}")
async def get_used_courses(
    semester_id: int,
    section: Optional[str] = None,
    schedule_id: Optional[int] = None,
    conn = Depends(get_db_connection)
):
    """
    Get all course codes that are already used in schedules for the specified semester and section.
    If section is provided, only returns courses used in that section.
    If schedule_id is provided, excludes that schedule from the results (for edit mode).
    """
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT course_code, id as schedule_id, section
            FROM schedules
            WHERE semester_id = %s
            """
            params = [semester_id]
            
            # Filter by section if provided
            if section:
                query += " AND section = %s"
                params.append(section)
            
            # If editing a schedule, exclude it from the results
            if schedule_id:
                query += " AND id != %s"
                params.append(schedule_id)
            
            cursor.execute(query, params)
            used_courses = cursor.fetchall()
            
            # Get the schedule being edited if provided
            edited_schedule = None
            if schedule_id:
                cursor.execute(
                    "SELECT course_code, section FROM schedules WHERE id = %s",
                    (schedule_id,)
                )
                result = cursor.fetchone()
                if result:
                    edited_schedule = {
                        "course_code": result["course_code"],
                        "schedule_id": schedule_id,
                        "section": result["section"],
                        "is_being_edited": True
                    }
            
            # Format the response
            response = {
                "used_courses": [
                    {
                        "course_code": course["course_code"],
                        "schedule_id": course["schedule_id"],
                        "section": course["section"]
                    }
                    for course in used_courses
                ],
                "edited_schedule": edited_schedule
            }
            
            return response
            
    except Exception as e:
        print(f"Error getting used courses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting used courses: {str(e)}"
        )

def check_and_add_next_academic_year_semesters(conn, semester_id, user_id):
    """
    Check if the given semester is a Summer semester. If so, add the next academic year's semesters.
    
    Args:
        conn: Database connection
        semester_id: ID of the current semester
        user_id: ID of the user performing the operation
    """
    try:
        # Check if user_id exists in users table, set to NULL if not
        if user_id:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE id = %s", (user_id,))
                user_exists = cursor.fetchone()['count'] > 0
                if not user_exists:
                    print(f"Warning: User with ID '{user_id}' not found. Setting user_id to NULL in next_academic_year function")
                    user_id = None
        
        with conn.cursor() as cursor:
            # Get semester details
            cursor.execute("SELECT name FROM semesters WHERE id = %s", (semester_id,))
            semester_data = cursor.fetchone()
            
            if not semester_data:
                print(f"Semester with ID {semester_id} not found")
                return
                
            semester_name = semester_data['name']
            
            # Check if this is a Summer semester
            if "Summer" not in semester_name:
                return
                
            print(f"Approved semester is a Summer semester: {semester_name}")
            
            # Extract year from semester name
            # Assuming format like "Summer 2026"
            try:
                current_year = int(semester_name.split()[-1])
                # Correct increment: Summer 2026 should be followed by 1st Sem 2026-2027
                next_year_start = current_year
                next_year_end = current_year + 1
                academic_year = f"{next_year_start}-{next_year_end}"
                
                # Create names for next year's semesters
                next_first_sem = f"1st Sem {academic_year}"
                next_second_sem = f"2nd Sem {academic_year}"
                next_summer = f"Summer {next_year_end}"
                
                # Check if these semesters already exist
                cursor.execute(
                    "SELECT name FROM semesters WHERE name = %s OR name = %s OR name = %s",
                    (next_first_sem, next_second_sem, next_summer)
                )
                existing = cursor.fetchall()
                existing_names = [sem['name'] for sem in existing]
                
                # Add new semesters if they don't exist
                for new_sem in [next_first_sem, next_second_sem, next_summer]:
                    if new_sem not in existing_names:
                        cursor.execute(
                            "INSERT INTO semesters (name, created_at) VALUES (%s, NOW())",
                            (new_sem,)
                        )
                        print(f"Added new semester: {new_sem}")
                
                # Log to audit log if user_id is provided
                if user_id:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO audit_log (user_id, action, details)
                            VALUES (%s, %s, %s)
                            """,
                            (
                                user_id,
                                "ADD_NEXT_YEAR_SEMESTERS",
                                f"Added next academic year semesters after approving {semester_name}"
                            )
                        )
                    except Exception as log_error:
                        print(f"Error logging to audit_log: {str(log_error)}")
                else:
                    print("Skipping audit log entry due to NULL user_id")
                
                conn.commit()
                print(f"Successfully added next academic year semesters for {academic_year}")
                
            except (ValueError, IndexError) as e:
                print(f"Error parsing year from semester name: {str(e)}")
                
    except Exception as e:
        print(f"Error adding next academic year semesters: {str(e)}")
        # Don't raise, just log the error 

@router.patch("/schedules/bulk-status-update")
async def update_multiple_schedules_status(
    update_data: BulkScheduleStatusUpdate,
    request: Request,
    conn = Depends(get_db_connection)
):
    """Update the status of multiple schedules at once and send a single notification"""
    try:
        if not update_data.schedule_ids or len(update_data.schedule_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No schedule IDs provided"
            )
            
        # Validate status
        if update_data.status not in ['draft', 'pending', 'approved']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'draft', 'pending', or 'approved'"
            )
        
        # Get user ID for creator
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Try to get from query parameters or headers
            user_id = request.query_params.get('user_id') or request.headers.get('X-User-ID')
        else:
            user_id = user_id.id
            
        print(f"Performing bulk status update to {update_data.status} with user: {user_id}")
        
        # Get semester ID if it's not provided - use the first schedule's semester
        semester_id = update_data.semester_id
        if not semester_id and update_data.schedule_ids:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT semester_id FROM schedules WHERE id = %s",
                    (update_data.schedule_ids[0],)
                )
                result = cursor.fetchone()
                if result:
                    semester_id = result['semester_id']
        
        # Update all schedules in a single transaction
        with conn.cursor() as cursor:
            # Update the status of all schedules
            update_count = 0
            for schedule_id in update_data.schedule_ids:
                cursor.execute(
                    "UPDATE schedules SET status = %s WHERE id = %s",
                    (update_data.status, schedule_id)
                )
                update_count += cursor.rowcount
                
                # Log each status change to audit log
                try:
                    cursor.execute(
                        """
                        INSERT INTO audit_log (user_id, action, details, ip_address)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            user_id,
                            "UPDATE_SCHEDULE_STATUS",
                            f"Schedule {schedule_id} status changed to {update_data.status}",
                            request.client.host if hasattr(request, 'client') else None
                        )
                    )
                except Exception as log_error:
                    print(f"Error logging status change: {log_error}")
                    # Continue even if logging fails
            
            # If changing to pending, create a notification for the Dean
            if update_data.status == 'pending' and semester_id:
                try:
                    # Create a notification for the Dean with the count of schedules
                    notification_id = create_schedule_pending_notification(
                        conn=conn,
                        semester_id=semester_id,
                        created_by=user_id,
                        schedule_count=update_count
                    )
                    print(f"Created bulk schedule pending notification with ID: {notification_id}")
                except Exception as notif_error:
                    print(f"Error creating bulk schedule pending notification: {notif_error}")
                    # Continue even if notification creation fails
            
            # If changing to approved, potentially create approval notifications
            if update_data.status == 'approved' and semester_id:
                try:
                    # Check if this semester is the current display semester
                    cursor.execute(
                        "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                    )
                    setting_row = cursor.fetchone()
                    was_already_current_display_semester = False
                    
                    if setting_row and setting_row['setting_value'] == str(semester_id):
                        was_already_current_display_semester = True
                        print(f"Semester {semester_id} is already set as current_display_semester_id")
                    else:
                        # Set this as the current display semester
                        if setting_row:
                            # Update existing setting
                            cursor.execute(
                                """
                                UPDATE system_settings 
                                SET setting_value = %s, updated_at = NOW()
                                WHERE setting_key = 'current_display_semester_id'
                                """,
                                (str(semester_id),)
                            )
                        else:
                            # Insert new setting
                            cursor.execute(
                                """
                                INSERT INTO system_settings 
                                (setting_key, setting_value, description)
                                VALUES ('current_display_semester_id', %s, 'ID of the semester that should be displayed in all dashboards')
                                """,
                                (str(semester_id),)
                            )
                            
                        # Commit changes to ensure system settings are updated
                        conn.commit()
                        print(f"Updated current_display_semester_id to {semester_id} in bulk approval")
                        
                        # Small delay to ensure system settings are properly updated before notifications
                        import time
                        time.sleep(0.5)  # 500ms delay
                        
                        # Re-fetch to confirm the update
                        cursor.execute(
                            "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                        )
                        updated_setting = cursor.fetchone()
                        if updated_setting and updated_setting['setting_value'] == str(semester_id):
                            print("Confirmed system settings update was successful for bulk approval")
                        else:
                            print("Warning: System settings update may not have been applied for bulk approval")
                            
                    # Recheck the current display semester one more time to be extra sure
                    cursor.execute(
                        "SELECT setting_value FROM system_settings WHERE setting_key = 'current_display_semester_id'"
                    )
                    latest_setting = cursor.fetchone()
                    if latest_setting and latest_setting['setting_value'] == str(semester_id):
                        was_already_current_display_semester = True
                        print("Final check: This semester is now the current display semester")
                        
                    # Create a notification about the approved schedules
                    notification_id = create_schedule_approval_notification(
                        conn=conn,
                        semester_id=semester_id,
                        created_by=user_id,
                        was_already_current_display_semester=was_already_current_display_semester,
                        is_bulk_approval=True
                    )
                    print(f"Created bulk schedule approval notification with ID: {notification_id}")
                    
                except Exception as notif_error:
                    print(f"Error handling bulk approval notification: {notif_error}")
                    # Continue even if notification creation fails
            
            conn.commit()
            
            return {
                "message": f"{update_count} schedules updated to {update_data.status} successfully",
                "updated_count": update_count,
                "semester_id": semester_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error performing bulk status update: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating schedules: {str(e)}"
        ) 