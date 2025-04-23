from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
import traceback

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection

router = APIRouter(tags=["system_settings"])

class SystemSettingUpdate(BaseModel):
    setting_value: str
    description: Optional[str] = None

@router.get("/system-settings/{setting_key}")
async def get_system_setting(
    setting_key: str,
    conn = Depends(get_db_connection)
):
    """Get a system setting by key"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM system_settings WHERE setting_key = %s",
                (setting_key,)
            )
            setting = cursor.fetchone()
            
            if not setting:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Setting with key '{setting_key}' not found"
                )
            
            return setting
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching system setting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching system setting"
        )

@router.put("/system-settings/{setting_key}")
async def update_system_setting(
    setting_key: str,
    setting_update: SystemSettingUpdate,
    request: Request,
    conn = Depends(get_db_connection)
):
    """Update a system setting by key"""
    try:
        # Get user ID from request state, or use default
        user_id = getattr(request.state, 'user', None)
        if user_id is None or not hasattr(user_id, 'id'):
            # Use NULL for updated_by if no user ID available
            user_id = None
        else:
            user_id = user_id.id
            
        with conn.cursor() as cursor:
            # Check if setting exists
            cursor.execute(
                "SELECT * FROM system_settings WHERE setting_key = %s",
                (setting_key,)
            )
            existing_setting = cursor.fetchone()
            
            if not existing_setting:
                # If setting doesn't exist, create it
                cursor.execute(
                    """
                    INSERT INTO system_settings 
                    (setting_key, setting_value, description, updated_by)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        setting_key,
                        setting_update.setting_value,
                        setting_update.description,
                        user_id
                    )
                )
                conn.commit()
                
                return {
                    "message": f"Setting '{setting_key}' created successfully",
                    "setting_key": setting_key,
                    "setting_value": setting_update.setting_value
                }
            
            # Update existing setting
            cursor.execute(
                """
                UPDATE system_settings
                SET setting_value = %s, 
                    description = COALESCE(%s, description),
                    updated_by = %s
                WHERE setting_key = %s
                """,
                (
                    setting_update.setting_value,
                    setting_update.description,
                    user_id,
                    setting_key
                )
            )
            conn.commit()
            
            return {
                "message": f"Setting '{setting_key}' updated successfully",
                "setting_key": setting_key,
                "setting_value": setting_update.setting_value
            }
    except Exception as e:
        conn.rollback()
        print(f"Error updating system setting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating system setting"
        )
        
@router.get("/system-settings/display-semester/current")
async def get_current_display_semester(
    conn = Depends(get_db_connection)
):
    """Get the current display semester with semester details"""
    try:
        with conn.cursor() as cursor:
            # Get the current display semester ID
            cursor.execute(
                """
                SELECT setting_value 
                FROM system_settings 
                WHERE setting_key = 'current_display_semester_id'
                """
            )
            setting = cursor.fetchone()
            
            if not setting:
                # If setting doesn't exist, use the default (1)
                semester_id = 1
                
                # Also insert the default setting since it doesn't exist
                print("No current_display_semester_id setting found, creating default with value 1")
                try:
                    cursor.execute(
                        """
                        INSERT INTO system_settings (setting_key, setting_value, description)
                        VALUES ('current_display_semester_id', '1', 'ID of the semester that should be displayed in all dashboards')
                        """
                    )
                    conn.commit()
                    print("Successfully created default current_display_semester_id setting")
                except Exception as setting_error:
                    print(f"Error creating default setting: {setting_error}")
                    # Continue even if this fails
            else:
                try:
                    semester_id = int(setting['setting_value'])
                    print(f"Found current_display_semester_id setting with value: {semester_id}")
                except (ValueError, TypeError) as e:
                    print(f"Invalid semester_id value in settings: {setting['setting_value']}, using default 1")
                    semester_id = 1
            
            # Get semester details
            cursor.execute(
                "SELECT * FROM semesters WHERE id = %s",
                (semester_id,)
            )
            semester = cursor.fetchone()
            
            if not semester:
                print(f"No semester found with ID {semester_id}, looking for an active semester")
                # If semester doesn't exist, get the first active semester
                cursor.execute(
                    "SELECT * FROM semesters WHERE is_active = TRUE ORDER BY id LIMIT 1"
                )
                semester = cursor.fetchone()
                
                # If no active semesters, get the first semester
                if not semester:
                    print("No active semesters found, getting the first semester")
                    cursor.execute(
                        "SELECT * FROM semesters ORDER BY id LIMIT 1"
                    )
                    semester = cursor.fetchone()
                
                # If still no semester, return error
                if not semester:
                    print("No semesters found in the system")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No semesters found in the system"
                    )
                
                new_semester_id = semester['id']
                print(f"Found semester with ID {new_semester_id}, updating current_display_semester_id")
                
                # Update the current display semester setting
                try:
                    cursor.execute(
                        """
                        INSERT INTO system_settings (setting_key, setting_value, description)
                        VALUES ('current_display_semester_id', %s, 'ID of the semester that should be displayed in all dashboards')
                        ON DUPLICATE KEY UPDATE setting_value = %s
                        """,
                        (str(new_semester_id), str(new_semester_id))
                    )
                    conn.commit()
                    print(f"Updated current_display_semester_id to {new_semester_id}")
                except Exception as update_error:
                    print(f"Error updating current_display_semester_id: {update_error}")
                    # Continue even if this fails
            
            return {
                "current_display_semester": semester,
                "semester_id": semester['id'],
                "semester_name": semester['name']
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching current display semester: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching current display semester"
        ) 