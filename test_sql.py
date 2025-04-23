import pymysql

def test_current_time_query():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='labclass_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Test with backticks
            cursor.execute("SELECT NOW() as `current_time`")
            result1 = cursor.fetchone()
            print("Result with backticks:", result1)
            
            # Test without backticks (which should fail)
            try:
                cursor.execute("SELECT NOW() as current_time")
                result2 = cursor.fetchone()
                print("Result without backticks:", result2)
            except Exception as e:
                print("Error without backticks:", e)
                
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    print("Testing SQL queries...")
    test_current_time_query() 