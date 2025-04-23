"""
Test script to verify the Dean notifications API endpoints
"""
import requests
import json

# API Configuration
API_URL = "http://localhost:8000/api"

def test_get_dean_notifications():
    """Test fetching notifications for the Dean user directly from the database"""
    print("\n=== Testing GET /dean-notifications endpoint ===")
    
    response = requests.get(f"{API_URL}/dean-notifications")
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        notifications = response.json()
        print(f"Successfully retrieved {len(notifications)} Dean notifications")
        
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
    """Test marking a notification as read for the Dean user"""
    print("\n=== Testing PATCH /dean-notifications/{notification_id}/read endpoint ===")
    
    # First, get an unread notification ID
    response = requests.get(f"{API_URL}/dean-notifications")
    
    if response.status_code == 200:
        notifications = response.json()
        unread_notifications = [n for n in notifications if not n['is_read']]
        
        if unread_notifications:
            notification_id = unread_notifications[0]['id']
            print(f"Found unread notification with ID: {notification_id}")
            
            # Mark the notification as read
            mark_response = requests.patch(f"{API_URL}/dean-notifications/{notification_id}/read")
            print(f"Status code: {mark_response.status_code}")
            
            if mark_response.status_code == 200:
                print(f"Successfully marked notification {notification_id} as read")
                print(f"Response: {mark_response.json()}")
            else:
                print(f"Error response: {mark_response.text}")
        else:
            print("No unread notifications found for Dean")
    else:
        print(f"Error fetching notifications: {response.text}")

def test_mark_all_as_read():
    """Test marking all notifications as read for the Dean user"""
    print("\n=== Testing PATCH /dean-notifications/read-all endpoint ===")
    
    response = requests.patch(f"{API_URL}/dean-notifications/read-all")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Successfully marked all Dean notifications as read")
        print(f"Response: {response.json()}")
    else:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    print("=== Dean Notifications API Test ===")
    
    # Test the endpoints
    test_get_dean_notifications()
    test_mark_notification_as_read()
    test_mark_all_as_read()
    
    print("\nTests completed!") 