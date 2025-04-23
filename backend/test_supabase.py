import requests
import json

# Supabase configurations
SUPABASE_URL = 'https://yfiyhsazgjsxjmybsyar.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlmaXloc2F6Z2pzeGpteWJzeWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4ODE5MzEsImV4cCI6MjA1ODQ1NzkzMX0.j7oFwaqYvJq45jhPuQBPEtNU-itU-CRleOJcqm1fOOo'

def check_supabase_connection():
    """Check connection to Supabase and display all tables"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        print("Checking Supabase connection...")
        
        # Try to list all tables
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/',
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Try to get schedules table structure
        print("\nChecking schedules table...")
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/schedules?limit=1',
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                print("Table structure:")
                for key in data[0].keys():
                    print(f"- {key}: {type(data[0][key]).__name__}")
            else:
                print("No records found, but table exists")
        else:
            print(f"Error: {response.text}")
            
        # Try to create a dummy record to see what fields are required
        print("\nTrying minimal record insert to see required fields...")
        test_data = {
            "id": 9999,  # Using a very high ID to avoid conflicts
            "semester": "Test Semester",
            "section": "Test Section",
            "course_code": "TEST101",
            "course_name": "Test Course",
            "day": "Monday",
            "lab_room": "Test Room",
            "instructor_name": "Test Instructor",
            "start_time": "08:00 AM",
            "end_time": "09:00 AM",
            "status": "draft",
            "class_type": "lab"
        }
        
        insert_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'  # Return the created record
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/schedules',
            headers=insert_headers,
            json=test_data
        )
        
        print(f"Insert response status: {response.status_code}")
        if response.status_code >= 400:
            print(f"Error: {response.text}")
        else:
            created_record = response.json()
            print(f"Created record: {json.dumps(created_record, indent=2)}")
            
            # Clean up by deleting the test record
            delete_response = requests.delete(
                f'{SUPABASE_URL}/rest/v1/schedules?id=eq.9999',
                headers=headers
            )
            print(f"Cleanup status: {delete_response.status_code}")
        
    except Exception as e:
        print(f"Error testing Supabase: {str(e)}")

if __name__ == "__main__":
    check_supabase_connection() 