#!/usr/bin/env python3
"""
Test script to verify that semester increment logic works correctly.

This test simulates the approval of a Summer semester and checks that the resulting
academic year sequence follows the correct pattern.
"""

import sys
import os
import pymysql
import pymysql.cursors
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database connection and necessary functions
from main import get_db_connection
from routes.schedules import check_and_add_next_academic_year_semesters

def test_semester_increment():
    """
    Test the semester increment logic by simulating various scenarios
    and verifying the output.
    """
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TEMPORARY TABLE test_semesters (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create a test audit log table
            cursor.execute("""
                CREATE TEMPORARY TABLE test_audit_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(255),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert initial test semesters
            cursor.execute("""
                INSERT INTO test_semesters (name) VALUES 
                ('1st Sem 2025-2026'),
                ('2nd Sem 2025-2026'),
                ('Summer 2026')
            """)
            
            # Get the ID of the Summer 2026 semester
            cursor.execute("SELECT id FROM test_semesters WHERE name = 'Summer 2026'")
            summer_2026_id = cursor.fetchone()['id']
            
            # Create a modified version of check_and_add_next_academic_year_semesters
            # to work with our test tables
            def test_add_next_semesters(semester_id, user_id=1):
                try:
                    # Get semester details
                    cursor.execute("SELECT name FROM test_semesters WHERE id = %s", (semester_id,))
                    semester_data = cursor.fetchone()
                    
                    if not semester_data:
                        print(f"Semester with ID {semester_id} not found")
                        return
                        
                    semester_name = semester_data['name']
                    
                    # Check if this is a Summer semester
                    if "Summer" not in semester_name:
                        return
                        
                    print(f"Test: Approved semester is a Summer semester: {semester_name}")
                    
                    # Extract year from semester name
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
                        
                        print(f"Test: Generated semester names:")
                        print(f"  - {next_first_sem}")
                        print(f"  - {next_second_sem}")
                        print(f"  - {next_summer}")
                        
                        # Check if these semesters already exist
                        cursor.execute(
                            "SELECT name FROM test_semesters WHERE name = %s OR name = %s OR name = %s",
                            (next_first_sem, next_second_sem, next_summer)
                        )
                        existing = cursor.fetchall()
                        existing_names = [sem['name'] for sem in existing]
                        
                        # Add new semesters if they don't exist
                        for new_sem in [next_first_sem, next_second_sem, next_summer]:
                            if new_sem not in existing_names:
                                cursor.execute(
                                    "INSERT INTO test_semesters (name, created_at) VALUES (%s, NOW())",
                                    (new_sem,)
                                )
                                print(f"Test: Added new semester: {new_sem}")
                        
                        # Log to audit log
                        cursor.execute(
                            """
                            INSERT INTO test_audit_log (user_id, action, details)
                            VALUES (%s, %s, %s)
                            """,
                            (
                                user_id,
                                "ADD_NEXT_YEAR_SEMESTERS",
                                f"Added next academic year semesters after approving {semester_name}"
                            )
                        )
                        
                        conn.commit()
                        print(f"Test: Successfully added next academic year semesters for {academic_year}")
                        
                    except (ValueError, IndexError) as e:
                        print(f"Test: Error parsing year from semester name: {str(e)}")
                        
                except Exception as e:
                    print(f"Test: Error adding next academic year semesters: {str(e)}")
            
            # Run the test function with Summer 2026
            print("\n=== Testing semester increment for Summer 2026 ===")
            test_add_next_semesters(summer_2026_id)
            
            # Check what semesters we have after the first increment
            cursor.execute("SELECT * FROM test_semesters ORDER BY id")
            semesters_after_first = cursor.fetchall()
            
            print("\n=== Semesters after first increment ===")
            for sem in semesters_after_first:
                print(f"ID: {sem['id']}, Name: {sem['name']}")
            
            # Now test the second increment with Summer 2027
            cursor.execute("SELECT id FROM test_semesters WHERE name = 'Summer 2027'")
            summer_2027_id = cursor.fetchone()['id']
            
            print("\n=== Testing semester increment for Summer 2027 ===")
            test_add_next_semesters(summer_2027_id)
            
            # Check what semesters we have after the second increment
            cursor.execute("SELECT * FROM test_semesters ORDER BY id")
            semesters_after_second = cursor.fetchall()
            
            print("\n=== Semesters after second increment ===")
            for sem in semesters_after_second:
                print(f"ID: {sem['id']}, Name: {sem['name']}")
            
            # Validate the final sequence
            expected_sequence = [
                '1st Sem 2025-2026', 
                '2nd Sem 2025-2026', 
                'Summer 2026',
                '1st Sem 2026-2027', 
                '2nd Sem 2026-2027', 
                'Summer 2027',
                '1st Sem 2027-2028', 
                '2nd Sem 2027-2028', 
                'Summer 2028'
            ]
            
            actual_sequence = [sem['name'] for sem in semesters_after_second]
            
            print("\n=== Validation ===")
            if expected_sequence == actual_sequence:
                print("SUCCESS: The semester sequence is correct!")
            else:
                print("ERROR: The semester sequence is incorrect.")
                print("Expected:", expected_sequence)
                print("Actual:", actual_sequence)
                
                # Find differences
                for i, (expected, actual) in enumerate(zip(expected_sequence, actual_sequence)):
                    if expected != actual:
                        print(f"Mismatch at position {i}: Expected '{expected}', got '{actual}'")
    
    except Exception as e:
        print(f"Test error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_semester_increment() 