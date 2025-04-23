import mysql.connector

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
    
    cursor = conn.cursor()
    
    # 1. Add missing columns if they don't exist
    # Get current columns
    cursor.execute("SHOW COLUMNS FROM users")
    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]
    
    # Check for missing columns
    if 'is_active' not in column_names:
        print("Adding is_active column")
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
    
    if 'is_approved' not in column_names:
        print("Adding is_approved column")
        cursor.execute("ALTER TABLE users ADD COLUMN is_approved BOOLEAN NOT NULL DEFAULT FALSE")
    
    if 'requires_approval' not in column_names:
        print("Adding requires_approval column")
        cursor.execute("ALTER TABLE users ADD COLUMN requires_approval BOOLEAN NOT NULL DEFAULT TRUE")
    
    # 2. Force update ALL users to be approved and active
    cursor.execute("""
    UPDATE users SET 
        is_approved = TRUE, 
        is_active = TRUE
    """)
    
    print(f"Updated {cursor.rowcount} users to be approved and active")
    
    # 3. Set all students to not require approval
    cursor.execute("""
    UPDATE users SET 
        requires_approval = FALSE
    WHERE role = 'Student'
    """)
    
    print(f"Updated {cursor.rowcount} student users to not require approval")
    
    # Ensure admin account is properly set up
    cursor.execute("""
    UPDATE users SET 
        is_approved = TRUE, 
        requires_approval = FALSE,
        is_active = TRUE
    WHERE id = 'admin' OR email = 'admin@uic.edu'
    """)
    
    print(f"Updated admin account status: {cursor.rowcount} rows affected")
    
    # Commit changes
    conn.commit()
    
    # Print all user statuses to verify
    cursor.execute("SELECT id, email, role, is_approved, requires_approval, is_active FROM users")
    users = cursor.fetchall()
    
    print("\n=== Current User Statuses ===")
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
        print(f"  is_approved: {user[3]}, requires_approval: {user[4]}, is_active: {user[5]}")
    
    print("\nAll users have been updated to be approved and active!")
    print("You should now be able to log in with any account.")
    
    # Close connections
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}") 