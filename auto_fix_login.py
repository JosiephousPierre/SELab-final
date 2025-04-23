import mysql.connector
import sys

# Database connection parameters
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Warweapons19"
DB_NAME = "labclass_db"

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Check if there are any issues with the table structure
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    column_names = [col['Field'] for col in columns]
    
    print("Table structure:")
    for col in columns:
        print(f"{col['Field']} - {col['Type']} - Null: {col['Null']} - Default: {col['Default']}")
    
    # Check for missing columns and add them if needed
    required_columns = ['is_active', 'is_approved', 'requires_approval']
    missing_columns = [col for col in required_columns if col not in column_names]
    
    for col in missing_columns:
        print(f"Adding missing column: {col}")
        if col == 'is_active':
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
        elif col == 'is_approved':
            cursor.execute("ALTER TABLE users ADD COLUMN is_approved BOOLEAN NOT NULL DEFAULT FALSE")
        elif col == 'requires_approval':
            cursor.execute("ALTER TABLE users ADD COLUMN requires_approval BOOLEAN NOT NULL DEFAULT TRUE")
    
    # Get all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print(f"\nFound {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}")
        print(f"  is_approved: {user.get('is_approved', 'Not set')}, requires_approval: {user.get('requires_approval', 'Not set')}, is_active: {user.get('is_active', 'Not set')}")
    
    # Fix all non-student accounts
    cursor.execute("""
    UPDATE users SET 
        is_approved = TRUE, 
        is_active = TRUE
    WHERE requires_approval = TRUE
    """)
    rows_updated = cursor.rowcount
    print(f"Fixed {rows_updated} users that required approval")
    
    # Set all student accounts to not require approval and approved
    cursor.execute("""
    UPDATE users SET 
        is_approved = TRUE, 
        requires_approval = FALSE,
        is_active = TRUE
    WHERE role = 'Student'
    """)
    rows_updated = cursor.rowcount
    print(f"Fixed {rows_updated} student accounts")
    
    # Make sure admin account is properly set up
    cursor.execute("""
    UPDATE users SET 
        is_approved = TRUE, 
        requires_approval = FALSE,
        is_active = TRUE
    WHERE id = 'admin' OR email = 'admin@uic.edu'
    """)
    rows_updated = cursor.rowcount
    print(f"Fixed admin account: {rows_updated} rows updated")
    
    conn.commit()
    
    # Verify the changes
    cursor.execute("SELECT * FROM users")
    updated_users = cursor.fetchall()
    
    print("\nUpdated user statuses:")
    for user in updated_users:
        print(f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}")
        print(f"  is_approved: {user.get('is_approved', 'Not set')}, requires_approval: {user.get('requires_approval', 'Not set')}, is_active: {user.get('is_active', 'Not set')}")
    
    print("\nAll users have been fixed. You should now be able to log in.")
    
    # Close connection
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}") 