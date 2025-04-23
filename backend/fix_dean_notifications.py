"""
Script to fix the Dean's notifications by ensuring global notifications are assigned properly.
"""
import pymysql
import sys
from datetime import datetime

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "labclass_db"

def main():
    # Connect to the database
    print("Connecting to database...")
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected successfully!")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    try:
        with conn.cursor() as cursor:
            # 1. Find Dean user(s) in the database
            cursor.execute("SELECT id, full_name, email FROM users WHERE role = 'Dean'")
            dean_users = cursor.fetchall()
            
            if not dean_users:
                print("No users with Dean role found in the database!")
                print("Creating a Dean user for testing...")
                
                # Create a Dean user for testing
                dean_id = "dean_test"
                dean_name = "Test Dean"
                dean_email = "dean@example.com"
                
                try:
                    # Check if user already exists
                    cursor.execute("SELECT id FROM users WHERE id = %s OR email = %s", (dean_id, dean_email))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        print(f"User with ID {dean_id} or email {dean_email} already exists!")
                        dean_id = existing_user['id']
                    else:
                        # Create new Dean user
                        cursor.execute("""
                            INSERT INTO users (id, full_name, email, password, role, is_approved, requires_approval)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (dean_id, dean_name, dean_email, "$2b$12$I42gD8WSUhcNyYDEhJKuaeVkTH/YmIYrK6j/TqwrC4RUaEIjLnzpy", "Dean", True, False))
                        conn.commit()
                        print(f"Created Dean user with ID: {dean_id}")
                    
                    # Use this Dean for further operations
                    dean_users = [{"id": dean_id, "full_name": dean_name, "email": dean_email}]
                except Exception as e:
                    print(f"Error creating Dean user: {e}")
                    return
            
            # 2. Process each Dean user
            for user in dean_users:
                dean_id = user['id']
                print(f"Processing Dean: {user['full_name']} (ID: {dean_id})")
                
                # 3. Ensure the Dean user exists in the users table
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE id = %s", (dean_id,))
                if cursor.fetchone()['count'] == 0:
                    print(f"WARNING: Dean ID {dean_id} does not exist in the users table!")
                    continue
                
                # 4. Check if the Dean has any notifications
                cursor.execute(
                    "SELECT COUNT(*) as count FROM user_notifications WHERE user_id = %s",
                    (dean_id,)
                )
                notification_count = cursor.fetchone()['count']
                print(f"Dean has {notification_count} notifications")
                
                # 5. Get all global notifications that should be visible to everyone
                cursor.execute(
                    "SELECT id FROM notifications WHERE is_global = TRUE"
                )
                global_notifications = cursor.fetchall()
                print(f"Found {len(global_notifications)} global notifications")
                
                # 6. For each global notification, ensure the Dean has an entry
                added_count = 0
                for notification in global_notifications:
                    notification_id = notification['id']
                    
                    # Check if the Dean already has this notification
                    cursor.execute(
                        """
                        SELECT COUNT(*) as count 
                        FROM user_notifications 
                        WHERE user_id = %s AND notification_id = %s
                        """,
                        (dean_id, notification_id)
                    )
                    
                    if cursor.fetchone()['count'] == 0:
                        # Dean doesn't have this notification, add it
                        try:
                            cursor.execute(
                                """
                                INSERT INTO user_notifications (user_id, notification_id, is_read) 
                                VALUES (%s, %s, FALSE)
                                """,
                                (dean_id, notification_id)
                            )
                            added_count += 1
                            print(f"Added notification {notification_id} to Dean {dean_id}")
                        except Exception as e:
                            print(f"Error adding notification {notification_id} to Dean: {e}")
                
                if added_count > 0:
                    conn.commit()
                    print(f"Added {added_count} missing notifications to Dean {dean_id}")
                else:
                    print("No new notifications needed to be added")
                    
                # 7. If no global notifications exist, create a test notification
                if len(global_notifications) == 0:
                    print("No global notifications found. Creating a test notification...")
                    
                    try:
                        # Create a test notification
                        cursor.execute(
                            """
                            INSERT INTO notifications 
                            (title, message, type, is_global, created_at) 
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                "Test Notification", 
                                "This is a test notification for the Dean user", 
                                "info", 
                                True, 
                                datetime.now()
                            )
                        )
                        
                        notification_id = cursor.lastrowid
                        print(f"Created test notification with ID: {notification_id}")
                        
                        # Assign it to the Dean
                        cursor.execute(
                            """
                            INSERT INTO user_notifications 
                            (user_id, notification_id, is_read) 
                            VALUES (%s, %s, FALSE)
                            """,
                            (dean_id, notification_id)
                        )
                        
                        conn.commit()
                        print(f"Assigned test notification {notification_id} to Dean {dean_id}")
                    except Exception as e:
                        conn.rollback()
                        print(f"Error creating test notification: {e}")
                
                print("\n" + "-"*50 + "\n")
                
            print("Processing complete!")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main() 