"""
Test script to verify the Academic Coordinator notifications API endpoints
"""
import requests
import json

# API Configuration
API_URL = "http://localhost:8000/api"

def test_get_acad_coor_notifications():
    """Test fetching notifications for the Academic Coordinator user directly from the database"""
    print("\n=== Testing GET /acad-coor-notifications endpoint ===")
    
    response = requests.get(f"{API_URL}/acad-coor-notifications")
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        notifications = response.json()
        print(f"Successfully retrieved {len(notifications)} Academic Coordinator notifications")
        
        # Print the first 3 notifications
        for i, notification in enumerate(notifications[:3]):
            print(f"\nNotification {i+1}:")
            print(f"  ID: {notification['id']}")
            print(f"  Title: {notification['title']}")
            print(f"  Message: {notification['message']}")
            print(f"  Created at: {notification['created_at']}")
            print(f"  Is read: {notification['is_read']}")
    else:
        print(f"Error response: {response.text}")

def test_mark_notification_as_read():
    """Test marking a notification as read for the Academic Coordinator user"""
    print("\n=== Testing PATCH /acad-coor-notifications/{notification_id}/read endpoint ===")
    
    # First, get an unread notification ID
    response = requests.get(f"{API_URL}/acad-coor-notifications")
    
    if response.status_code == 200:
        notifications = response.json()
        unread_notifications = [n for n in notifications if not n['is_read']]
        
        if unread_notifications:
            notification_id = unread_notifications[0]['id']
            print(f"Found unread notification with ID: {notification_id}")
            
            # Mark the notification as read
            mark_response = requests.patch(f"{API_URL}/acad-coor-notifications/{notification_id}/read")
            print(f"Status code: {mark_response.status_code}")
            
            if mark_response.status_code == 200:
                print(f"Successfully marked notification {notification_id} as read")
                print(f"Response: {mark_response.json()}")
            else:
                print(f"Error response: {mark_response.text}")
        else:
            print("No unread notifications found for Academic Coordinator")
    else:
        print(f"Error fetching notifications: {response.text}")

def test_mark_all_as_read():
    """Test marking all notifications as read for the Academic Coordinator user"""
    print("\n=== Testing PATCH /acad-coor-notifications/read-all endpoint ===")
    
    response = requests.patch(f"{API_URL}/acad-coor-notifications/read-all")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Successfully marked all Academic Coordinator notifications as read")
        print(f"Response: {response.json()}")
    else:
        print(f"Error response: {response.text}")

def test_clear_all_notifications():
    """Test clearing all notifications for the Academic Coordinator user"""
    print("\n=== Testing DELETE /acad-coor-notifications/clear-all endpoint ===")
    
    # Ask for confirmation before running this test since it permanently deletes data
    confirm = input("This will permanently clear all Academic Coordinator notifications. Continue? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Test skipped.")
        return
    
    response = requests.delete(f"{API_URL}/acad-coor-notifications/clear-all")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Successfully cleared all Academic Coordinator notifications")
        print(f"Response: {response.json()}")
    else:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    print("=== Academic Coordinator Notifications API Test ===")
    
    # Test the endpoints
    test_get_acad_coor_notifications()
    test_mark_notification_as_read()
    test_mark_all_as_read()
    # Uncomment to test clearing all notifications (requires confirmation)
    # test_clear_all_notifications()
    
    print("\nTests completed!") 