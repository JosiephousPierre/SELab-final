import mysql.connector
import getpass

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
    
    # Get user email/ID to check
    user_identifier = input("Enter the user email or ID to check: ")
    
    # Check if user exists
    cursor.execute(
        "SELECT * FROM users WHERE id = %s OR email = %s", 
        (user_identifier, user_identifier)
    )
    user = cursor.fetchone()
    
    if not user:
        print(f"No user found with ID or email: {user_identifier}")
    else:
        print("\n=== User Information ===")
        print(f"ID: {user['id']}")
        print(f"Full Name: {user['full_name']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
        print(f"Is Approved: {user.get('is_approved', 'Not set')}")
        print(f"Requires Approval: {user.get('requires_approval', 'Not set')}")
        print(f"Is Active: {user.get('is_active', 'Not set')}")
        print(f"Date Created: {user.get('date_created', 'Not set')}")
        print(f"Last Login: {user.get('last_login', 'Not set')}")
        
        # Ask if we should fix this user
        print("\nDo you want to fix this user's account? (y/n)")
        fix_choice = input().strip().lower()
        
        if fix_choice == 'y':
            # Fix the user
            cursor.execute("""
            UPDATE users SET 
                is_approved = TRUE, 
                is_active = TRUE
            WHERE id = %s OR email = %s
            """, (user_identifier, user_identifier))
            
            if cursor.rowcount > 0:
                print(f"Updated user account - is_approved=TRUE, is_active=TRUE")
                
                # Verify the changes
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s OR email = %s", 
                    (user_identifier, user_identifier)
                )
                updated_user = cursor.fetchone()
                
                print("\n=== Updated User Information ===")
                print(f"ID: {updated_user['id']}")
                print(f"Is Approved: {updated_user.get('is_approved', 'Not set')}")
                print(f"Requires Approval: {updated_user.get('requires_approval', 'Not set')}")
                print(f"Is Active: {updated_user.get('is_active', 'Not set')}")
                
                # Check password
                print("\nDo you want to test this user's password? (y/n)")
                check_pwd = input().strip().lower()
                
                if check_pwd == 'y':
                    import bcrypt
                    
                    # Enter password to test
                    pwd = getpass.getpass("Enter the password to test: ")
                    
                    # Get hashed password from database
                    hashed_pwd = updated_user['password']
                    
                    # Verify password
                    try:
                        valid = bcrypt.checkpw(pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))
                        if valid:
                            print("✅ Password matches! You should be able to log in now.")
                        else:
                            print("❌ Password does not match the stored hash.")
                            
                            # Ask to reset password
                            print("\nDo you want to reset this user's password? (y/n)")
                            reset_pwd = input().strip().lower()
                            
                            if reset_pwd == 'y':
                                new_pwd = getpass.getpass("Enter new password: ")
                                confirm_pwd = getpass.getpass("Confirm new password: ")
                                
                                if new_pwd == confirm_pwd:
                                    # Hash the new password
                                    hashed_password = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                    
                                    # Update password
                                    cursor.execute(
                                        "UPDATE users SET password = %s WHERE id = %s OR email = %s",
                                        (hashed_password, user_identifier, user_identifier)
                                    )
                                    
                                    print("Password has been reset successfully!")
                                else:
                                    print("Passwords do not match. No changes made.")
                    except Exception as e:
                        print(f"Error verifying password: {e}")
            
            conn.commit()
        
        else:
            print("No changes were made to the user account.")
    
    # Close connection
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}") 