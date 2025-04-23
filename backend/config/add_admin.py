import mysql.connector
import bcrypt

# Database connection parameters
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Warweapons19"  # This is from your main.py file - change if needed
DB_NAME = "labclass_db"

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")
    
    # Create users table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        is_approved BOOLEAN NOT NULL DEFAULT FALSE,
        requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
        date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME NULL
    )
    """)
    
    # Check if is_active column exists, if not add it
    cursor.execute("""
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE 
        TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'is_active'
    """, (DB_NAME,))
    
    column_exists = cursor.fetchone()[0]
    
    if column_exists == 0:
        print("Adding is_active column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
        print("Column added successfully.")
    
    # Hash the admin password
    admin_password = get_password_hash('admin123')
    
    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE id = 'admin'")
    admin_exists = cursor.fetchone()
    
    if admin_exists:
        # Update admin if it exists
        cursor.execute("""
        UPDATE users SET 
            full_name = 'System Administrator',
            email = 'admin@uic.edu',
            password = %s,
            role = 'System Administrator',
            is_approved = TRUE,
            requires_approval = FALSE,
            is_active = TRUE
        WHERE id = 'admin'
        """, (admin_password,))
        print("Admin account updated successfully!")
    else:
        # Add admin account
        cursor.execute("""
        INSERT INTO users 
            (id, full_name, email, password, role, is_approved, requires_approval, is_active) 
        VALUES 
            ('admin', 'System Administrator', 'admin@uic.edu', %s, 'System Administrator', TRUE, FALSE, TRUE)
        """, (admin_password,))
        print("Admin account created successfully!")
    
    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Database setup complete.")
    print("You can now use admin/admin123 credentials to log in.")
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}") 