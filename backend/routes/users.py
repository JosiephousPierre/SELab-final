from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional
import pymysql
from datetime import datetime
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import from main app - update to absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection, User, get_password_hash, verify_password
from routes.auth import send_approval_email  # Import only the approval email function

router = APIRouter(tags=["users"])

class UserBase(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    is_approved: bool
    requires_approval: bool
    date_created: str
    last_login: Optional[str] = None
    is_active: bool = True
    year_section: Optional[str] = None

class UserList(BaseModel):
    users: List[UserBase]

class ApproveUserRequest(BaseModel):
    is_approved: Optional[int] = 1
    requires_approval: Optional[int] = 0

@router.get("/users/pending-approval", response_model=UserList)
async def get_pending_users(
    conn = Depends(get_db_connection)
):
    # Get all users pending approval
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM users 
                WHERE requires_approval = TRUE AND is_approved = FALSE
                ORDER BY date_created DESC
                """
            )
            users = cursor.fetchall()
        
        # Print debugging info
        print(f"Found {len(users)} pending users")
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        print(f"Error in get_pending_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending users: {str(e)}"
        )

@router.get("/users/all", response_model=UserList)
async def get_all_users(
    conn = Depends(get_db_connection)
):
    # Get all users
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY date_created DESC")
            users = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.put("/users/{user_id}/approve")
async def approve_user(
    user_id: str,
    approval_data: ApproveUserRequest,
    request: Request,
    conn = Depends(get_db_connection)
):
    # Check if user exists and requires approval
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", 
            (user_id,)
        )
        user = cursor.fetchone()
    
    if not user:
        print(f"User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Debug info
    print(f"Found user to approve: {user['id']}, requires_approval: {user['requires_approval']}, is_approved: {user['is_approved']}")
    
    if not user["requires_approval"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user type does not require approval"
        )
    
    if user["is_approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already approved"
        )
    
    # Approve the user
    try:
        is_approved_value = True if approval_data.is_approved == 1 else False
        requires_approval_value = False if approval_data.requires_approval == 0 else True
        
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_approved = %s, requires_approval = %s, is_active = TRUE WHERE id = %s",
                (is_approved_value, requires_approval_value, user_id)
            )
            
            # Check if "system" user exists, otherwise use NULL for the audit log
            cursor.execute("SELECT id FROM users WHERE id = 'system'")
            system_user = cursor.fetchone()
            audit_user_id = system_user['id'] if system_user else None
            
            # Log the approval event
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    audit_user_id,
                    "APPROVAL",
                    f"Approved user: {user_id}", 
                    client_ip
                )
            )
            
        conn.commit()
        
        # If the user has one of the instructor roles, sync with instructors table
        if user["role"] in ['Academic Coordinator', 'Dean', 'Faculty/Staff']:
            try:
                # Import httpx for making internal API calls
                import httpx
                
                # Make an internal API call to sync instructors
                async with httpx.AsyncClient() as client:
                    # Call our own API endpoint to sync instructors
                    response = await client.post(
                        "http://localhost:8000/api/instructors/sync"
                    )
                    
                    if response.status_code != 200:
                        print(f"Warning: Failed to sync instructors after user approval: {response.text}")
            except Exception as e:
                # Don't fail the whole request if sync fails
                print(f"Warning: Exception while syncing instructors: {str(e)}")
        
        # Send approval notification email
        try:
            send_approval_email(user["email"], user["full_name"], user["role"])
        except Exception as e:
            # Log the error but don't fail the approval process if email sending fails
            print(f"Warning: Failed to send approval email: {str(e)}")
        
        return {"message": f"User {user_id} has been approved"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve user: {str(e)}"
        )

@router.get("/users/me", response_model=UserBase)
async def get_current_user_info():
    # Return system user info since we've removed authentication
    return {
        "id": "system",
        "full_name": "System User",
        "email": "system@example.com",
        "role": "System Administrator",
        "is_approved": True,
        "requires_approval": False,
        "date_created": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True
    }

@router.get("/users/approved", response_model=UserList)
async def get_approved_users(
    conn = Depends(get_db_connection)
):
    # Get all approved users
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM users 
                WHERE is_approved = TRUE
                ORDER BY date_created DESC
                """
            )
            users = cursor.fetchall()
        
        # Print debugging info
        print(f"Found {len(users)} approved users")
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        print(f"Error in get_approved_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve approved users: {str(e)}"
        )

@router.get("/users/{user_id}/profile", response_model=UserBase)
async def get_user_profile(
    user_id: str,
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove password for security
        if "password" in user:
            del user["password"]
            
        # Convert datetime objects to strings for JSON serialization
        if user.get("date_created"):
            user["date_created"] = user["date_created"].isoformat()
        if user.get("last_login"):
            user["last_login"] = user["last_login"].isoformat()
        
        # Ensure all required fields are present
        if "is_approved" not in user:
            user["is_approved"] = True
        if "requires_approval" not in user:
            user["requires_approval"] = True if user["role"] != "Student" else False
        if "is_active" not in user:
            user["is_active"] = True
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )

# Special debug route that bypasses authentication for profile access
@router.get("/users/{user_id}/debug-profile")
async def get_user_profile_debug(
    user_id: str,
    request: Request,
    conn = Depends(get_db_connection)
):
    print(f"DEBUG PROFILE: Accessing profile for user_id={user_id} without auth")
    print(f"DEBUG PROFILE: Client IP={request.client.host}")
    
    try:
        with conn.cursor() as cursor:
            print(f"DEBUG PROFILE: Executing query for user_id={user_id}")
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            print(f"DEBUG PROFILE: User not found for id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print(f"DEBUG PROFILE: User found: {user['id']}, {user['email']}")
        
        # Convert datetime objects to strings for JSON serialization
        if user.get("date_created"):
            user["date_created"] = user["date_created"].isoformat()
        if user.get("last_login"):
            user["last_login"] = user["last_login"].isoformat()
        
        # Ensure all required fields are present
        if "is_approved" not in user:
            user["is_approved"] = True
        if "requires_approval" not in user:
            user["requires_approval"] = True if user["role"] != "Student" else False
        if "is_active" not in user:
            user["is_active"] = True
        
        # Remove password field for security
        if "password" in user:
            del user["password"]
            
        return user
    except Exception as e:
        print(f"DEBUG PROFILE: Error in debug profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    year_section: Optional[str] = None
    
@router.put("/users/{user_id}/profile", response_model=UserBase)
async def update_user_profile(
    user_id: str,
    profile_data: UserProfileUpdate,
    conn = Depends(get_db_connection)
):
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        update_fields = {}
        if profile_data.full_name is not None:
            update_fields["full_name"] = profile_data.full_name
        if profile_data.email is not None:
            # Check if email already exists for another user
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE email = %s AND id != %s", 
                    (profile_data.email, user_id)
                )
                existing_user = cursor.fetchone()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
            update_fields["email"] = profile_data.email
            
        # Add year_section field update if provided (only applies to students)
        if profile_data.year_section is not None:
            # For debugging, print this info to see what's happening
            print(f"User role: {user['role']}")
            print(f"Received year_section: {profile_data.year_section}")
            
            # Always include year_section in update fields if provided
            update_fields["year_section"] = profile_data.year_section
            print(f"Added year_section to update fields: {update_fields}")
        
        # Only update if there are fields to update
        if update_fields:
            set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
            values = list(update_fields.values())
            values.append(user_id)
            
            # Generate and log the actual SQL query for debugging
            sql_query = f"UPDATE users SET {set_clause} WHERE id = %s"
            print(f"EXECUTING SQL: {sql_query}")
            print(f"SQL VALUES: {values}")
            
            with conn.cursor() as cursor:
                cursor.execute(sql_query, values)
                # Force commit to ensure changes are saved
                conn.commit()
                print(f"Update query executed and committed")
                # Verify rows affected
                print(f"Rows affected: {cursor.rowcount}")
            
            # Verify the update by fetching the user again
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s", 
                    (user_id,)
                )
                updated_user = cursor.fetchone()
                
                # Print updated user for debugging
                print(f"Updated user after commit: {updated_user}")
                print(f"Updated year_section value: {updated_user.get('year_section')}")
                
                # Convert datetime objects to strings for JSON serialization
                if updated_user["date_created"]:
                    updated_user["date_created"] = updated_user["date_created"].isoformat()
                if updated_user["last_login"]:
                    updated_user["last_login"] = updated_user["last_login"].isoformat()
                
                # Make sure year_section is included in response, even if NULL
                if "year_section" not in updated_user:
                    updated_user["year_section"] = None
            
            return updated_user
        
        # If no updates were made, return the original user
        # Convert datetime objects to strings for JSON serialization
        if user["date_created"]:
            user["date_created"] = user["date_created"].isoformat()
        if user["last_login"]:
            user["last_login"] = user["last_login"].isoformat()
            
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"ERROR in update_user_profile: {str(e)}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

# Password change endpoint
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/users/{user_id}/change-password", response_model=dict)
async def change_password(
    user_id: str,
    password_data: PasswordChangeRequest,
    conn = Depends(get_db_connection)
):
    try:
        # Find the user whose password will be changed
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Skip current password check since we're removing auth

        # Update the password
        hashed_password = get_password_hash(password_data.new_password)
        
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (hashed_password, user_id)
            )
            conn.commit()
            
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

# Update user role
class UserRoleUpdate(BaseModel):
    role: str
    
@router.put("/users/{user_id}/role", response_model=UserBase)
async def update_user_role(
    user_id: str,
    update_data: UserRoleUpdate,
    request: Request,
    conn = Depends(get_db_connection)
):
    # Verify the new role is valid
    valid_roles = ["System Administrator", "Academic Coordinator", "Lab InCharge", 
                  "Dean", "Faculty/Staff", "Student"]
    if update_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        # Find the user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get current role before update
        previous_role = user["role"]
        
        # Update the role
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (update_data.role, user_id)
            )
            conn.commit()
            
        # Get the ID of the user who made the change (from request state)
        acting_user_id = getattr(request.state, 'user', None)
        if acting_user_id and hasattr(acting_user_id, 'id'):
            acting_user_id = acting_user_id.id
        else:
            # If not available in request state, try to get from headers
            acting_user_id = request.headers.get('X-User-ID')
        
        # Only create notification if the role was actually changed
        if previous_role != update_data.role:
            # Import and use the notification function
            from routes.notifications import create_role_change_notification
            
            notification_id = create_role_change_notification(
                conn=conn,
                user_id=user_id,
                new_role=update_data.role,
                created_by=acting_user_id
            )
            
            if notification_id:
                print(f"Created notification {notification_id} for role change")
            else:
                print("Failed to create notification for role change")
        
        # Add user to the forced logout list to automatically log them out
        with conn.cursor() as cursor:
            # Get current timestamp
            cursor.execute("SELECT NOW() as `current_time`")
            result = cursor.fetchone()
            current_time = result["current_time"]
            
            # Check if the user is already in the force_logout table
            cursor.execute(
                "SELECT * FROM forced_logouts WHERE user_id = %s",
                (user_id,)
            )
            existing_logout = cursor.fetchone()
            
            if existing_logout:
                # Update the timestamp
                cursor.execute(
                    "UPDATE forced_logouts SET timestamp = %s WHERE user_id = %s",
                    (current_time, user_id)
                )
            else:
                # Insert a new entry
                cursor.execute(
                    "INSERT INTO forced_logouts (user_id, timestamp) VALUES (%s, %s)",
                    (user_id, current_time)
                )
            
            conn.commit()
            print(f"User {user_id} added to forced logout list at {current_time}")
        
        # Get updated user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

# Add a new endpoint to check if a user is forced to logout
@router.get("/users/{user_id}/check-forced-logout")
async def check_forced_logout(
    user_id: str,
    last_auth_time: Optional[str] = None,
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            # First get the user's current data
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Query to check if there's a forced logout timestamp newer than last_auth_time
            query = """
                SELECT id, timestamp FROM forced_logouts 
                WHERE user_id = %s
            """
            params = [user_id]
            
            if last_auth_time:
                # Add condition to check if the forced logout timestamp is newer
                query += " AND timestamp > %s"
                params.append(last_auth_time)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            should_logout = result is not None
            
            # If a result is found, remove the entry after sending the logout signal
            # This ensures the user is only logged out once per modification
            if should_logout:
                logout_id = result["id"]
                cursor.execute(
                    "DELETE FROM forced_logouts WHERE id = %s",
                    (logout_id,)
                )
                conn.commit()
                print(f"Removed forced logout entry {logout_id} for user {user_id} after processing")
            
            # Return the result with user information
            return {
                "should_logout": should_logout,
                "timestamp": result["timestamp"].isoformat() if result else None,
                "user_info": {
                    "id": user.get("id"),
                    "role": user.get("role"),
                    "is_active": user.get("is_active")
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check forced logout status: {str(e)}"
        )

# Deactivate user
@router.put("/users/{user_id}/deactivate", response_model=UserBase)
async def deactivate_user(
    user_id: str,
    request: Request,
    conn = Depends(get_db_connection)
):
    try:
        # Find the user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deactivating the last system admin
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as admin_count FROM users WHERE role = 'System Administrator' AND is_active = 1"
            )
            result = cursor.fetchone()
            
        if user["role"] == "System Administrator" and result["admin_count"] <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active System Administrator"
            )
        
        # Update the user
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = 0 WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        
        # Add user to the forced logout list
        with conn.cursor() as cursor:
            # Get current timestamp
            cursor.execute("SELECT NOW() as `current_time`")
            result = cursor.fetchone()
            current_time = result["current_time"]
            
            # Check if the user is already in the force_logout table
            cursor.execute(
                "SELECT * FROM forced_logouts WHERE user_id = %s",
                (user_id,)
            )
            existing_logout = cursor.fetchone()
            
            if existing_logout:
                # Update the timestamp
                cursor.execute(
                    "UPDATE forced_logouts SET timestamp = %s WHERE user_id = %s",
                    (current_time, user_id)
                )
            else:
                # Insert a new entry
                cursor.execute(
                    "INSERT INTO forced_logouts (user_id, timestamp) VALUES (%s, %s)",
                    (user_id, current_time)
                )
            
            conn.commit()
            print(f"User {user_id} added to forced logout list at {current_time} due to deactivation")
        
        # Get updated user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

# Activate user
@router.put("/users/{user_id}/activate", response_model=UserBase)
async def activate_user(
    user_id: str,
    conn = Depends(get_db_connection)
):
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Activate the user - no need to force logout in this case
        # as the user would have to login again anyway
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = TRUE WHERE id = %s",
                (user_id,)
            )
            conn.commit()
            
            # Remove any forced logout entries for this user since they'll need to log in again
            cursor.execute(
                "DELETE FROM forced_logouts WHERE user_id = %s",
                (user_id,)
            )
            conn.commit()
            print(f"Removed any forced logout entries for user {user_id} during activation")
        
        # Get updated user data
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

# Delete user
@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    conn = Depends(get_db_connection)
):
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete the user
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        
        return {"message": f"User {user_id} has been deleted"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.delete("/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    request: Request,
    conn = Depends(get_db_connection)
):
    # Check if user exists and requires approval
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", 
            (user_id,)
        )
        user = cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store user info for email notification before deletion
    user_email = user["email"]
    user_name = user["full_name"]
    user_role = user["role"]
    
    # Delete the user from the database
    try:
        with conn.cursor() as cursor:
            # First delete the user
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            
            # Then log the rejection event (after user is deleted to avoid FK constraint)
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    None,  # Using NULL instead of "system" to avoid FK constraint
                    "REJECTION",
                    f"Rejected and deleted user: {user_id} ({user_name})", 
                    client_ip
                )
            )
            
        conn.commit()
        
        # Send rejection notification email (after DB transaction is committed)
        try:
            send_rejection_email(user_email, user_name, user_role)
        except Exception as e:
            # Log the error but don't fail the whole request if email sending fails
            print(f"Warning: Failed to send rejection email: {str(e)}")
            
        return {"message": f"User {user_id} has been rejected and removed from the system"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject user: {str(e)}"
        )

def send_rejection_email(email, name, role):
    """Helper function to send an account rejection notification email."""
    # Using the same email configuration as in approval emails
    smtp_server = "smtp.gmail.com"
    smtp_port = "587"
    smtp_username = "pierredosdos@gmail.com"
    smtp_password = "bibb iylk bqkc grez"  # Using the same password as in the approval email function
    
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Account Application Status"
        message["From"] = smtp_username
        message["To"] = email
        
        # Plain text version
        text = f"""
Hello {name},

We regret to inform you that your application for a {role} account in the UIC Lab Class Scheduler has been rejected.

If you believe this is an error or would like to discuss this further, please contact the system administrator.

Best regards,
The UIC Lab Class Scheduler Team
"""
        
        # HTML version
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #DD385A; color: white; padding: 10px 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Account Application Status</h2>
        </div>
        <div class="content">
            <p>Hello {name},</p>
            <p>We regret to inform you that your application for a <strong>{role}</strong> account in the UIC Lab Class Scheduler has been rejected.</p>
            <p>If you believe this is an error or would like to discuss this further, please contact the system administrator.</p>
            <div class="footer">
                <p>Best regards,<br>The UIC Lab Class Scheduler Team</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, email, message.as_string())
        
        print(f"Account rejection email sent to {email}")
    except Exception as e:
        print(f"Error sending rejection email: {str(e)}")
        # Don't raise the exception here, just log it
        # This ensures the rejection process continues even if email sending fails

# Special endpoint to directly fix a user
@router.get("/fix-user/{user_id}")
async def fix_user(
    user_id: str,
    conn = Depends(get_db_connection)
):
    print(f"FIX USER: Attempting to fix user with ID {user_id}")
    
    try:
        # First check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            print(f"FIX USER: User with ID {user_id} not found")
            return {"message": f"User with ID {user_id} not found"}
        
        # Update the user to ensure they are approved and active
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users SET 
                    is_approved = TRUE, 
                    requires_approval = FALSE,
                    is_active = TRUE
                WHERE id = %s
                """,
                (user_id,)
            )
            conn.commit()
        
        # Verify the update
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        return {
            "message": f"User {user_id} has been fixed",
            "status": {
                "before": {
                    "is_approved": user.get("is_approved", None),
                    "requires_approval": user.get("requires_approval", None),
                    "is_active": user.get("is_active", None)
                },
                "after": {
                    "is_approved": updated_user.get("is_approved", None),
                    "requires_approval": updated_user.get("requires_approval", None), 
                    "is_active": updated_user.get("is_active", None)
                }
            }
        }
    except Exception as e:
        print(f"FIX USER: Error fixing user {user_id}: {str(e)}")
        return {"error": f"Failed to fix user: {str(e)}"}

@router.get("/roles", response_model=dict)
async def get_roles(conn = Depends(get_db_connection)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT role FROM role_permissions")
            # Make sure to convert row tuples to strings
            roles = [row["role"] for row in cursor.fetchall()]
            return {"roles": roles}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch roles: {str(e)}"
        )

# New model for student year_section update
class StudentYearSectionUpdate(BaseModel):
    year_section: str
    
# New endpoint specifically for year_section updates
@router.put("/users/{user_id}/year-section", response_model=UserBase)
async def update_student_year_section(
    user_id: str,
    update_data: StudentYearSectionUpdate,
    conn = Depends(get_db_connection)
):
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Debug prints for troubleshooting
        print(f"Updating year_section via dedicated endpoint for user {user_id}")
        print(f"Current role: {user['role']}")
        print(f"New year_section value: {update_data.year_section}")
        
        # Update the year_section without any role check
        with conn.cursor() as cursor:
            sql_query = "UPDATE users SET year_section = %s WHERE id = %s"
            print(f"EXECUTING SQL: {sql_query}")
            print(f"SQL VALUES: [{update_data.year_section}, {user_id}]")
            
            cursor.execute(
                sql_query,
                (update_data.year_section, user_id)
            )
            conn.commit()
            print(f"Update query executed and committed")
            print(f"Rows affected: {cursor.rowcount}")
        
        # Verify the update by fetching the user again
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
            
            # Print updated user for debugging
            print(f"Updated user after commit: {updated_user}")
            print(f"Updated year_section value: {updated_user.get('year_section')}")
            
            # Convert datetime objects to strings for JSON serialization
            if updated_user["date_created"]:
                updated_user["date_created"] = updated_user["date_created"].isoformat()
            if updated_user["last_login"]:
                updated_user["last_login"] = updated_user["last_login"].isoformat()
            
            # Make sure year_section is included in response
            if "year_section" not in updated_user:
                updated_user["year_section"] = None
        
        return updated_user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"ERROR in update_student_year_section: {str(e)}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update year section: {str(e)}"
        ) 