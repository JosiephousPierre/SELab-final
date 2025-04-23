import requests
import json

# Supabase configurations
SUPABASE_URL = 'https://yfiyhsazgjsxjmybsyar.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlmaXloc2F6Z2pzeGpteWJzeWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4ODE5MzEsImV4cCI6MjA1ODQ1NzkzMX0.j7oFwaqYvJq45jhPuQBPEtNU-itU-CRleOJcqm1fOOo'

def check_supabase_data():
    """Check the records in Supabase to see if they have been synced correctly"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        print("Checking Supabase schedules data...")
        
        # Get all schedules
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/schedules',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} records in Supabase")
            
            if data:
                # Print each record with focus on the created_by field
                for record in data:
                    print(f"\nRecord ID: {record.get('id')}")
                    print(f"  Course: {record.get('course_code')} - {record.get('course_name')}")
                    print(f"  Section: {record.get('section')}")
                    print(f"  Days: {record.get('day')} / {record.get('second_day')}")
                    print(f"  Lab Room: {record.get('lab_room')}")
                    print(f"  Created By: {record.get('created_by')}")  # This is the field we're most interested in
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error checking Supabase data: {str(e)}")

if __name__ == "__main__":
    check_supabase_data() 