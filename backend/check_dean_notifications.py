"""
Script to check if the Dean user has notifications in the database.
"""
import pymysql
import sys

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
            # Find Dean user(s) in the database
            cursor.execute("SELECT id, full_name, email FROM users WHERE role = 'Dean'")
            dean_users = cursor.fetchall()
            
            if not dean_users:
                print("No users with Dean role found in the database!")
                return
            
            print(f"Found {len(dean_users)} Dean user(s):")
            for user in dean_users:
                print(f"Dean ID: {user['id']}, Name: {user['full_name']}, Email: {user['email']}")
                
                # Check all notifications in the system
                cursor.execute("SELECT COUNT(*) as count FROM notifications")
                result = cursor.fetchone()
                print(f"Total notifications in the database: {result['count']}")
                
                # Check if this Dean has any notifications
                cursor.execute(
                    """
                    SELECT COUNT(*) as count 
                    FROM user_notifications 
                    WHERE user_id = %s
                    """, 
                    (user['id'],)
                )
                result = cursor.fetchone()
                print(f"Total notifications for Dean {user['id']}: {result['count']}")
                
                # List the notifications this Dean should receive
                cursor.execute(
                    """
                    SELECT n.id, n.title, n.message, n.type, n.is_global, n.created_at, 
                           un.is_read, un.read_at
                    FROM notifications n
                    JOIN user_notifications un ON n.id = un.notification_id
                    WHERE un.user_id = %s
                    ORDER BY n.created_at DESC
                    """,
                    (user['id'],)
                )
                dean_notifications = cursor.fetchall()
                
                if dean_notifications:
                    print(f"Found {len(dean_notifications)} notifications for Dean {user['id']}:")
                    for notification in dean_notifications:
                        print(f"  - ID: {notification['id']}")
                        print(f"    Title: {notification['title']}")
                        print(f"    Message: {notification['message']}")
                        print(f"    Type: {notification['type']}")
                        print(f"    Created: {notification['created_at']}")
                        print(f"    Read: {'Yes' if notification['is_read'] else 'No'}")
                        print()
                else:
                    print(f"No notifications found for Dean {user['id']}!")
                    
                    # Check if there are global notifications that the Dean should have received
                    cursor.execute(
                        """
                        SELECT id, title, message, is_global, created_at 
                        FROM notifications 
                        WHERE is_global = TRUE
                        ORDER BY created_at DESC
                        """
                    )
                    global_notifications = cursor.fetchall()
                    
                    if global_notifications:
                        print(f"Found {len(global_notifications)} global notifications that should have been sent to Dean:")
                        for notification in global_notifications:
                            print(f"  - ID: {notification['id']}")
                            print(f"    Title: {notification['title']}")
                            print(f"    Message: {notification['message']}")
                            print(f"    Created: {notification['created_at']}")
                            print()
                            
                        # Check if the Dean's ID is valid
                        cursor.execute("SELECT id FROM users WHERE id = %s", (user['id'],))
                        if not cursor.fetchone():
                            print(f"WARNING: Dean user ID '{user['id']}' does not exist in the users table!")
                    else:
                        print("No global notifications found in the system.")
                
                print("\n" + "-"*50 + "\n")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main() 