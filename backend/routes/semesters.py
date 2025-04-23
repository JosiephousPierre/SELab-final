from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection

router = APIRouter(tags=["semesters"])

class SemesterModel(BaseModel):
    id: int
    name: str
    created_at: str

@router.get("/semesters", response_model=List[SemesterModel])
async def get_semesters(conn = Depends(get_db_connection)):
    """
    Get all semesters from the database.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM semesters ORDER BY id")
            semesters = cursor.fetchall()
            
            # Convert datetime objects to strings
            for semester in semesters:
                if isinstance(semester['created_at'], datetime):
                    semester['created_at'] = semester['created_at'].isoformat()
            
            return semesters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching semesters: {str(e)}"
        )

# Removed the get_active_semesters endpoint since the is_active field no longer exists
# This functionality is now consolidated with the main get_semesters endpoint 