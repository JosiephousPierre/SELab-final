import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # Replace with your actual MySQL password
DB_NAME = "labclass_db"

# Connect to the database
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # Check semesters table
        cursor.execute("SELECT id, name, is_active FROM semesters")
        semesters = cursor.fetchall()
        print("\nSemesters:")
        for semester in semesters:
            print(f"ID: {semester['id']}, Name: {semester['name']}, Active: {semester['is_active']}")
        
        # Check lab_rooms table
        cursor.execute("SELECT id, name FROM lab_rooms")
        lab_rooms = cursor.fetchall()
        print("\nLab Rooms:")
        for lab_room in lab_rooms:
            print(f"ID: {lab_room['id']}, Name: {lab_room['name']}")
        
        # Check audit_log table
        cursor.execute("SHOW TABLES LIKE 'audit_log'")
        audit_log_exists = cursor.fetchone() is not None
        print(f"\nAudit Log Table Exists: {audit_log_exists}")
        
        if audit_log_exists:
            cursor.execute("DESCRIBE audit_log")
            columns = cursor.fetchall()
            print("\nAudit Log Columns:")
            for column in columns:
                print(f"Name: {column['Field']}, Type: {column['Type']}, Null: {column['Null']}")
        
        # Check schedules table
        cursor.execute("SHOW TABLES LIKE 'schedules'")
        schedules_exists = cursor.fetchone() is not None
        print(f"\nSchedules Table Exists: {schedules_exists}")
        
        if schedules_exists:
            cursor.execute("DESCRIBE schedules")
            columns = cursor.fetchall()
            print("\nSchedules Columns:")
            for column in columns:
                print(f"Name: {column['Field']}, Type: {column['Type']}, Null: {column['Null']}")
        
finally:
    connection.close()

print("\nDatabase check complete!") 