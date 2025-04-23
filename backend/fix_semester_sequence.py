#!/usr/bin/env python3
"""
Fix semester sequence in the database.

This script updates semester names that were incorrectly sequenced,
specifically fixing the years in the academic progression.

The sequence should be:
1. 1st Sem 2025-2026
2. 2nd Sem 2025-2026
3. Summer 2026
4. 1st Sem 2026-2027 (was 1st Sem 2027-2028)
5. 2nd Sem 2026-2027 (was 2nd Sem 2027-2028)
6. Summer 2027 (was Summer 2028)
"""

import sys
import os
import pymysql
import pymysql.cursors

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database connection from main application
from main import get_db_connection

def fix_semester_sequence():
    """
    Update the semester names to follow the correct sequence.
    """
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            # First, check the current semesters in the database
            cursor.execute("SELECT id, name FROM semesters ORDER BY id")
            semesters = cursor.fetchall()
            
            print("Current semesters in database:")
            for sem in semesters:
                print(f"ID: {sem['id']}, Name: {sem['name']}")
            
            # Identify incorrect semester names
            incorrect_mappings = [
                {"id": 55, "old_name": "1st Sem 2027-2028", "new_name": "1st Sem 2026-2027"},
                {"id": 56, "old_name": "2nd Sem 2027-2028", "new_name": "2nd Sem 2026-2027"},
                {"id": 57, "old_name": "Summer 2028", "new_name": "Summer 2027"}
            ]
            
            # Verify each mapping before updating
            for mapping in incorrect_mappings:
                cursor.execute("SELECT id, name FROM semesters WHERE id = %s", (mapping["id"],))
                current = cursor.fetchone()
                
                if not current:
                    print(f"Warning: Semester with ID {mapping['id']} not found")
                    continue
                    
                if current["name"] != mapping["old_name"]:
                    print(f"Warning: Expected '{mapping['old_name']}' but found '{current['name']}' for ID {mapping['id']}")
                    continue
                
                # Update the semester name
                cursor.execute(
                    "UPDATE semesters SET name = %s WHERE id = %s",
                    (mapping["new_name"], mapping["id"])
                )
                
                print(f"Updated semester ID {mapping['id']}: '{mapping['old_name']}' -> '{mapping['new_name']}'")
            
            # Commit changes
            conn.commit()
            
            # Verify the updates
            cursor.execute("SELECT id, name FROM semesters ORDER BY id")
            updated_semesters = cursor.fetchall()
            
            print("\nUpdated semesters in database:")
            for sem in updated_semesters:
                print(f"ID: {sem['id']}, Name: {sem['name']}")
                
            print("\nSemester sequence fixed successfully!")
            
    except Exception as e:
        print(f"Error fixing semester sequence: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_semester_sequence() 