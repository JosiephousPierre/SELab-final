import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="labclass_db",
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Insert each new instructor from the users table
        try:
            cursor.execute(
                "INSERT INTO instructors (user_id, full_name, email, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                ("2000", "Michel Bolo", "mich@example.com", "Faculty/Staff", 1)
            )
            print("Michel Bolo added")
        except Exception as e:
            print(f"Error adding Michel Bolo: {str(e)}")
        
        try:
            cursor.execute(
                "INSERT INTO instructors (user_id, full_name, email, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                ("2001", "Ian Benablo", "ian@example.com", "Dean", 1)
            )
            print("Ian Benablo added")
        except Exception as e:
            print(f"Error adding Ian Benablo: {str(e)}")
        
        try:
            cursor.execute(
                "INSERT INTO instructors (user_id, full_name, email, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                ("2002", "Popos Dosdos", "popos@example.com", "Academic Coordinator", 1)
            )
            print("Popos Dosdos added")
        except Exception as e:
            print(f"Error adding Popos Dosdos: {str(e)}")
    
    # Commit the transaction
    conn.commit()
    print("All new instructors added successfully!")
finally:
    conn.close() 