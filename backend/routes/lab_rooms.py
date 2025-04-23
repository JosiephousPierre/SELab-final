from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Import from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection

router = APIRouter(tags=["lab_rooms"])

class LabRoomModel(BaseModel):
    id: int
    name: str
    capacity: Optional[int] = None
    created_at: str

@router.get("/lab-rooms", response_model=List[LabRoomModel])
async def get_lab_rooms(conn = Depends(get_db_connection)):
    """
    Get all lab rooms from the database.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM lab_rooms ORDER BY id")
            lab_rooms = cursor.fetchall()
            
            # Convert datetime objects to strings
            for room in lab_rooms:
                if isinstance(room['created_at'], datetime):
                    room['created_at'] = room['created_at'].isoformat()
            
            return lab_rooms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching lab rooms: {str(e)}"
        ) 