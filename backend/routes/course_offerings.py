from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import pymysql
from datetime import datetime

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection

router = APIRouter(tags=["course_offerings"])

class CourseOfferingBase(BaseModel):
    code: str
    name: str
    year_and_section: str
    semester_id: int

class CourseOfferingCreate(CourseOfferingBase):
    pass

class CourseOfferingList(BaseModel):
    courses: List[CourseOfferingBase]

@router.post("/course-offerings/import", response_model=dict)
async def import_course_offerings(
    courses: List[CourseOfferingCreate],
    conn = Depends(get_db_connection)
):
    try:
        imported_count = 0
        with conn.cursor() as cursor:
            for course in courses:
                # Check if course already exists
                cursor.execute(
                    """
                    SELECT id FROM course_offerings 
                    WHERE code = %s AND year_and_section = %s AND semester_id = %s
                    """,
                    (course.code, course.year_and_section, course.semester_id)
                )
                existing_course = cursor.fetchone()
                
                if not existing_course:
                    # Insert new course
                    cursor.execute(
                        """
                        INSERT INTO course_offerings 
                        (code, name, year_and_section, semester_id, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            course.code,
                            course.name,
                            course.year_and_section,
                            course.semester_id,
                            datetime.now()
                        )
                    )
                    imported_count += 1
        
        conn.commit()
        return {"message": f"Successfully imported {imported_count} courses"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import courses: {str(e)}"
        )

@router.get("/course-offerings", response_model=CourseOfferingList)
async def get_course_offerings(
    semester_id: Optional[int] = None,
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM course_offerings WHERE 1=1"
            params = []
            
            if semester_id is not None:
                query += " AND semester_id = %s"
                params.append(semester_id)
            
            cursor.execute(query, params)
            courses = cursor.fetchall()
            
            return {"courses": courses}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch course offerings: {str(e)}"
        )

@router.delete("/course-offerings/all", response_model=dict)
async def delete_all_course_offerings(
    conn = Depends(get_db_connection)
):
    try:
        with conn.cursor() as cursor:
            # Get the count of course offerings for the response
            cursor.execute("SELECT COUNT(*) as count FROM course_offerings")
            count_result = cursor.fetchone()
            count = count_result['count'] if count_result else 0
            
            # Delete all course offerings
            cursor.execute("DELETE FROM course_offerings")
            
        conn.commit()
        return {"message": f"Successfully deleted {count} course offerings"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course offerings: {str(e)}"
        ) 