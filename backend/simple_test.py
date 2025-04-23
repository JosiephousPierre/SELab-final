import requests
import json

# Supabase configurations
SUPABASE_URL = 'https://yfiyhsazgjsxjmybsyar.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlmaXloc2F6Z2pzeGpteWJzeWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4ODE5MzEsImV4cCI6MjA1ODQ1NzkzMX0.j7oFwaqYvJq45jhPuQBPEtNU-itU-CRleOJcqm1fOOo'

print("Testing simple insertion to Supabase...")

# Create a simple test record
test_data = {
    "id": 9999,
    "semester": "Test Semester",
    "section": "Test Section",
    "course_code": "TEST101",
    "course_name": "Test Course",
    "day": "Monday",
    "lab_room": "Test Room",
    "instructor_name": "Test Instructor",
    "start_time": "08:00 AM",
    "end_time": "09:00 AM",
    "schedule_types": ["lab"],
    "status": "draft",
    "class_type": "lab"
}

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

try:
    # Try to insert the record
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/schedules',
        headers=headers,
        json=test_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    
    if response.status_code >= 400:
        print("INSERTION FAILED")
    else:
        print("INSERTION SUCCEEDED")
        
        # Clean up by deleting the test record
        delete_response = requests.delete(
            f'{SUPABASE_URL}/rest/v1/schedules?id=eq.9999',
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
        )
        print(f"Cleanup status: {delete_response.status_code}")
        
except Exception as e:
    print(f"Error: {str(e)}")

# Try retrieving table info
print("\nRetrieving table information...")
try:
    info_response = requests.get(
        f'{SUPABASE_URL}/rest/v1/schedules?limit=1',
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
    )
    print(f"Info response status: {info_response.status_code}")
    
    if info_response.status_code == 200:
        data = info_response.json()
        if data and len(data) > 0:
            print("Table structure:")
            for key in data[0].keys():
                print(f"- {key}")
        else:
            print("Table exists but no records found")
    else:
        print(f"Error: {info_response.text}")
except Exception as e:
    print(f"Error: {str(e)}") 