import pymysql
import sys
import os

def check_semesters():
    """Check all semesters in the database and their relationships"""
    # Database configuration
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_NAME = "labclass_db"
    
    print("Connecting to database...")
    try:
        # Connect to database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Connected to database successfully.")
        
        with conn.cursor() as cursor:
            # Get all semesters
            cursor.execute("SELECT * FROM semesters ORDER BY id")
            semesters = cursor.fetchall()
            
            print(f"\nFound {len(semesters)} semesters:")
            for sem in semesters:
                print(f"ID: {sem['id']}, Name: {sem['name']}, Created: {sem['created_at']}")
            
            # Check for Summer 2026
            cursor.execute("SELECT * FROM semesters WHERE name LIKE '%Summer 2026%'")
            summer_2026 = cursor.fetchone()
            
            if summer_2026:
                print(f"\nFound Summer 2026 with ID: {summer_2026['id']}")
                
                # Check if 2027-2028 semesters exist
                cursor.execute("SELECT * FROM semesters WHERE name LIKE '%2027-2028%'")
                semesters_2027_2028 = cursor.fetchall()
                
                print(f"\nFound {len(semesters_2027_2028)} semesters for 2027-2028:")
                for sem in semesters_2027_2028:
                    print(f"ID: {sem['id']}, Name: {sem['name']}")
                
                # Check Summer 2028
                cursor.execute("SELECT * FROM semesters WHERE name LIKE '%Summer 2028%'")
                summer_2028 = cursor.fetchone()
                
                if summer_2028:
                    print(f"\nFound Summer 2028 with ID: {summer_2028['id']}")
                else:
                    print("\nSummer 2028 not found")
            else:
                print("\nSummer 2026 not found")
            
            # Check approved schedules
            cursor.execute("""
                SELECT s.id, sem.name AS semester_name, s.status
                FROM schedules s 
                JOIN semesters sem ON s.semester_id = sem.id
                WHERE s.status = 'approved'
            """)
            approved_schedules = cursor.fetchall()
            
            print(f"\nFound {len(approved_schedules)} approved schedules:")
            for sched in approved_schedules:
                print(f"Schedule ID: {sched['id']}, Semester: {sched['semester_name']}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_semesters() 