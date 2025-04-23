import pymysql
import requests
import json
from datetime import datetime
import time
import schedule

# Database configurations - matching your current database.py setup
DB_HOST = "localhost"
DB_USER = "root" 
DB_PASSWORD = ""
DB_NAME = "labclass_db"

# Supabase configurations
SUPABASE_URL = 'https://yfiyhsazgjsxjmybsyar.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlmaXloc2F6Z2pzeGpteWJzeWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4ODE5MzEsImV4cCI6MjA1ODQ1NzkzMX0.j7oFwaqYvJq45jhPuQBPEtNU-itU-CRleOJcqm1fOOo'

# Column mapping from MySQL view to Supabase
# This maps the column names from the MySQL view to the Supabase table columns
COLUMN_MAPPING = {
    'id': 'id',
    'semester': 'semester',
    'section': 'section',
    'course_code': 'course_code',
    'course_name': 'course_name',
    'day': 'day',
    'second_day': 'second_day',
    'lab_room': 'lab_room',
    'instructor_name': 'instructor_name',
    'start_time': 'start_time',
    'end_time': 'end_time',
    'schedule_types': 'schedule_types',
    'status': 'status',
    'class_type': 'class_type',
    'created_by': 'created_by',
    'created_at': 'created_at',
    'updated_at': 'updated_at'
}

def get_mysql_schedules():
    """Fetch all schedules from MySQL schedules_with_names view"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            query = "SELECT * FROM schedules_with_names"
            cursor.execute(query)
            schedules = cursor.fetchall()
            
            # Convert any datetime objects to strings
            for schedule in schedules:
                for key, value in schedule.items():
                    if isinstance(value, datetime):
                        schedule[key] = value.isoformat()
                    elif isinstance(value, bytes):
                        try:
                            # Try to convert JSON strings
                            schedule[key] = json.loads(value.decode('utf-8'))
                        except:
                            schedule[key] = value.decode('utf-8')
            
        connection.close()
        return schedules
    except Exception as e:
        print(f"Error fetching MySQL schedules: {str(e)}")
        return []

def get_supabase_schedules():
    """Fetch all schedules from Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/schedules',
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Supabase schedules: {str(e)}")
        return []

def map_schedule_for_supabase(schedule):
    """Map the MySQL schedule to Supabase format"""
    supabase_schedule = {}
    for mysql_col, supabase_col in COLUMN_MAPPING.items():
        if mysql_col in schedule:
            # Include created_by field now that it's a varchar in Supabase
            supabase_schedule[supabase_col] = schedule[mysql_col]
    
    # Special handling for schedule_types field - ensure it's never null
    if 'schedule_types' in supabase_schedule:
        if isinstance(supabase_schedule['schedule_types'], str):
            try:
                # Try to parse as JSON
                supabase_schedule['schedule_types'] = json.loads(supabase_schedule['schedule_types'])
            except:
                # If not valid JSON, convert to array with the string
                supabase_schedule['schedule_types'] = [supabase_schedule['schedule_types']]
        elif supabase_schedule['schedule_types'] is None:
            # Set default value if null
            supabase_schedule['schedule_types'] = []
    else:
        # If schedule_types is missing, add an empty array
        supabase_schedule['schedule_types'] = []

    return supabase_schedule

def insert_supabase_schedule(schedule):
    """Insert a new schedule into Supabase"""
    try:
        # Map the schedule to Supabase format
        supabase_schedule = map_schedule_for_supabase(schedule)
        
        # Debug output
        print(f"Inserting schedule {schedule['id']} with data: {json.dumps(supabase_schedule)}")
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/schedules',
            headers=headers,
            json=supabase_schedule
        )
        
        # Print detailed error information
        if response.status_code >= 400:
            print(f"Error response status: {response.status_code}")
            print(f"Error response headers: {response.headers}")
            print(f"Error response text: {response.text}")
            # Try to parse as JSON if possible
            try:
                error_json = response.json()
                print(f"Error response JSON: {json.dumps(error_json, indent=2)}")
            except:
                pass
        
        response.raise_for_status()
        print(f"Successfully inserted schedule {schedule['id']}")
    except Exception as e:
        print(f"Error inserting schedule {schedule['id']}: {str(e)}")
        # Print the full data being sent for debugging
        print(f"Full data attempted to send: {json.dumps(supabase_schedule, indent=2)}")

def update_supabase_schedule(schedule_id, schedule):
    """Update an existing schedule in Supabase"""
    try:
        # Map the schedule to Supabase format
        supabase_schedule = map_schedule_for_supabase(schedule)
        
        # Debug output
        print(f"Updating schedule {schedule_id} with data: {json.dumps(supabase_schedule)}")
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/schedules?id=eq.{schedule_id}',
            headers=headers,
            json=supabase_schedule
        )
        
        if response.status_code >= 400:
            print(f"Error response: {response.text}")
            
        response.raise_for_status()
        print(f"Successfully updated schedule {schedule_id}")
    except Exception as e:
        print(f"Error updating schedule {schedule_id}: {str(e)}")

def delete_supabase_schedule(schedule_id):
    """Delete a schedule from Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Prefer': 'return=minimal'
        }
        response = requests.delete(
            f'{SUPABASE_URL}/rest/v1/schedules?id=eq.{schedule_id}',
            headers=headers
        )
        
        if response.status_code >= 400:
            print(f"Error response: {response.text}")
            
        response.raise_for_status()
        print(f"Successfully deleted schedule {schedule_id}")
    except Exception as e:
        print(f"Error deleting schedule {schedule_id}: {str(e)}")

def sync_databases():
    """Main function to synchronize the databases"""
    print(f"Starting database synchronization at {datetime.now()}")
    
    # Get schedules from both databases
    mysql_schedules = get_mysql_schedules()
    supabase_schedules = get_supabase_schedules()
    
    print(f"Found {len(mysql_schedules)} schedules in MySQL")
    print(f"Found {len(supabase_schedules)} schedules in Supabase")
    
    # Debug: Print sample MySQL schedule
    if mysql_schedules:
        print(f"Sample MySQL schedule: {json.dumps(mysql_schedules[0])}")
    
    # Create dictionaries for easier comparison
    mysql_dict = {str(schedule['id']): schedule for schedule in mysql_schedules}
    supabase_dict = {str(schedule['id']): schedule for schedule in supabase_schedules}
    
    # Find schedules to insert, update, or delete
    mysql_ids = set(mysql_dict.keys())
    supabase_ids = set(supabase_dict.keys())
    
    # Schedules to insert (in MySQL but not in Supabase)
    insert_count = 0
    for schedule_id in mysql_ids - supabase_ids:
        insert_supabase_schedule(mysql_dict[schedule_id])
        insert_count += 1
    
    # Schedules to update (in both but potentially different)
    update_count = 0
    for schedule_id in mysql_ids & supabase_ids:
        mysql_schedule = mysql_dict[schedule_id]
        supabase_schedule = supabase_dict[schedule_id]
        
        # Get mapped MySQL schedule
        mapped_mysql_schedule = map_schedule_for_supabase(mysql_schedule)
        
        # Compare relevant fields and update if different
        needs_update = False
        for key in mapped_mysql_schedule:
            if key in supabase_schedule and mapped_mysql_schedule[key] != supabase_schedule[key]:
                needs_update = True
                break
        
        if needs_update:
            update_supabase_schedule(schedule_id, mysql_schedule)
            update_count += 1
    
    # Schedules to delete (in Supabase but not in MySQL)
    delete_count = 0
    for schedule_id in supabase_ids - mysql_ids:
        delete_supabase_schedule(schedule_id)
        delete_count += 1
    
    print(f"Sync summary: {insert_count} inserted, {update_count} updated, {delete_count} deleted")
    print(f"Database synchronization completed at {datetime.now()}")

def run_scheduler():
    """Run the scheduler to sync databases periodically"""
    # Schedule the sync to run every 1 minute
    schedule.every(1).minutes.do(sync_databases)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

def get_supabase_table_structure():
    """Get the structure of the Supabase table to understand what fields are required"""
    try:
        print("Checking Supabase table structure...")
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Get a single row to check the structure
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/schedules?limit=1',
            headers=headers
        )
        
        if response.status_code == 200 and response.json():
            sample = response.json()[0]
            print(f"Supabase table columns: {', '.join(sample.keys())}")
        else:
            # Try to get the table definition
            print("No data found. Attempting to get table structure...")
            
    except Exception as e:
        print(f"Error checking Supabase table structure: {str(e)}")

if __name__ == "__main__":
    # Check Supabase table structure
    get_supabase_table_structure()
    
    # Run initial sync
    sync_databases()
    
    # Start the scheduler
    run_scheduler() 