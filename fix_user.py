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
    
    cursor = conn.cursor(dictionary=True)
    
    # Get the user details
    email = "laurence1@uic.edu.ph"  # Replace with the actual email
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if user:
        print(f"User found: {user['id']}, {user['email']}")
        print(f"Current status: is_approved={user['is_approved']}, requires_approval={user['requires_approval']}, is_active={user.get('is_active', 'Not set')}")
        
        # Fix the user account
        cursor.execute("""
        UPDATE users SET 
            is_approved = TRUE, 
            is_active = TRUE
        WHERE email = %s
        """, (email,))
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        updated_user = cursor.fetchone()
        
        print(f"Updated status: is_approved={updated_user['is_approved']}, requires_approval={updated_user['requires_approval']}, is_active={updated_user.get('is_active', 'Not set')}")
        print("User account has been fixed. You should now be able to log in.")
    else:
        print(f"User with email {email} not found.")
    
    # Close connection
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}") 