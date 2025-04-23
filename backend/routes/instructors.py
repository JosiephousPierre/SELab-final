from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection, get_current_active_user

router = APIRouter(tags=["instructors"])

class InstructorModel(BaseModel):
    id: int
    user_id: Optional[str] = None
    full_name: str
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: bool
    created_at: str

class InstructorCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    role: Optional[str] = None

@router.get("/instructors", response_model=List[InstructorModel])
async def get_instructors(
    conn = Depends(get_db_connection)
):
    """
    Get all instructors.
    """
    instructors = []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, full_name, email, role, is_active, created_at
                FROM instructors
                """
            )
            instructors = cursor.fetchall()
            
            # Convert datetime objects to strings
            for instructor in instructors:
                if isinstance(instructor['created_at'], datetime):
                    instructor['created_at'] = instructor['created_at'].isoformat()
            
            return instructors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching instructors: {str(e)}"
        )

@router.post("/instructors", response_model=InstructorModel)
async def create_instructor(
    instructor: InstructorCreate = Body(...),
    conn = Depends(get_db_connection)
):
    """
    Add a new instructor to the database.
    """
    try:
        with conn.cursor() as cursor:
            # Insert the new instructor
            cursor.execute(
                """
                INSERT INTO instructors (full_name, email, role, is_active)
                VALUES (%s, %s, %s, TRUE)
                """,
                (instructor.full_name, instructor.email, instructor.role)
            )
            
            # Get the ID of the newly inserted instructor
            new_id = cursor.lastrowid
            
            # Commit the transaction
            conn.commit()
            
            # Fetch the complete instructor data
            cursor.execute("SELECT * FROM instructors WHERE id = %s", (new_id,))
            new_instructor = cursor.fetchone()
            
            # Convert datetime to string
            if isinstance(new_instructor['created_at'], datetime):
                new_instructor['created_at'] = new_instructor['created_at'].isoformat()
            
            return new_instructor
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating instructor: {str(e)}"
        )

@router.post("/instructors/sync", response_model=List[InstructorModel])
async def sync_instructors(
    conn = Depends(get_db_connection)
):
    """
    Sync instructors from the users table. Get users 
    with role INSTRUCTOR, ADMIN, Dean, etc and add them to the instructors table
    regardless of approval status.
    """
    try:
        with conn.cursor() as cursor:
            # First, update roles for existing instructors
            cursor.execute(
                """
                UPDATE instructors i
                JOIN users u ON i.user_id = u.id
                SET i.role = u.role
                WHERE i.user_id IS NOT NULL
                """
            )
            updated_count = cursor.rowcount
            print(f"Updated roles for {updated_count} existing instructors")
            
            # Find users with specific roles who aren't already in instructors table
            # Removed the is_approved filter
            cursor.execute(
                """
                SELECT u.* FROM users u
                LEFT JOIN instructors i ON u.id = i.user_id
                WHERE u.role IN ('Academic Coordinator', 'Dean', 'Faculty/Staff')
                AND i.id IS NULL
                """
            )
            eligible_users = cursor.fetchall()
            
            # Add each eligible user as an instructor
            added_count = 0
            added_instructors = []
            for user in eligible_users:
                cursor.execute(
                    """
                    INSERT INTO instructors (user_id, full_name, email, role, is_active)
                    VALUES (%s, %s, %s, %s, TRUE)
                    """,
                    (user['id'], user['full_name'], user['email'], user['role'])
                )
                
                # Get the newly added instructor
                new_id = cursor.lastrowid
                cursor.execute("SELECT * FROM instructors WHERE id = %s", (new_id,))
                new_instructor = cursor.fetchone()
                
                # Convert datetime to string
                if isinstance(new_instructor['created_at'], datetime):
                    new_instructor['created_at'] = new_instructor['created_at'].isoformat()
                
                added_instructors.append(new_instructor)
                added_count += 1
            
            # Commit the transaction
            conn.commit()
            
            # If no instructors were added, return all active instructors
            if added_count == 0:
                cursor.execute(
                    """
                    SELECT id, user_id, full_name, email, role, is_active, created_at
                    FROM instructors
                    WHERE is_active = TRUE
                    """
                )
                all_instructors = cursor.fetchall()
                
                # Convert datetime objects to strings
                for instructor in all_instructors:
                    if isinstance(instructor['created_at'], datetime):
                        instructor['created_at'] = instructor['created_at'].isoformat()
                
                return all_instructors
            
            return added_instructors
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing instructors from users: {str(e)}"
        )

@router.get("/instructors/active", response_model=List[InstructorModel])
async def get_active_instructors(
    conn = Depends(get_db_connection)
):
    """
    Get all active instructors.
    """
    instructors = []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, full_name, email, role, is_active, created_at
                FROM instructors
                WHERE is_active = TRUE
                """
            )
            instructors = cursor.fetchall()
            
            # Convert datetime objects to strings
            for instructor in instructors:
                if isinstance(instructor['created_at'], datetime):
                    instructor['created_at'] = instructor['created_at'].isoformat()
            
            return instructors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching active instructors: {str(e)}"
        ) 