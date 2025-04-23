import pymysql
import requests

def test_api_endpoint():
    """Test if the roles API endpoint is working"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/roles')
        print("API Response Status:", response.status_code)
        print("API Response Content:", response.text)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def test_database_direct():
    """Test if we can query the database directly"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='labclass_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Test with DictCursor
            cursor.execute("SELECT role FROM role_permissions")
            results = cursor.fetchall()
            print("DictCursor Results:", results)
            
            # Test both ways of accessing data
            if results:
                first_row = results[0]
                try:
                    print("Accessing via index:", first_row[0])
                except Exception as e:
                    print("Error accessing via index:", e)
                
                try:
                    print("Accessing via key:", first_row["role"])
                except Exception as e:
                    print("Error accessing via key:", e)
            
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    print("Testing roles functionality...")
    api_results = test_api_endpoint()
    print("\nTesting database access directly...")
    test_database_direct()
    
    print("\nComparing results:")
    if api_results:
        print("API returned", len(api_results["roles"]), "roles") 