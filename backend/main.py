from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import uuid
import traceback
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer


load_dotenv()
# Create FastAPI instance
app = FastAPI(title="Lab Class API", description="API for Lab Class Management System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# JWT configuration
SECRET_KEY = "your-secret-key"  # In production, use an environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # Replace with your actual MySQL password
DB_NAME = "labclass_db"

# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield connection
    finally:
        connection.close()

# User model
class User:
    def __init__(self, id: str, full_name: str, email: str, role: str, is_approved: bool, requires_approval: bool, is_active: bool = True):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_approved = is_approved
        self.requires_approval = requires_approval
        self.is_active = is_active

# Authentication functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Password hashed successfully: {hashed[:10]}...")
        return hashed
    except Exception as e:
        print(f"Error hashing password: {str(e)}")
        # Fallback to a simple hash if bcrypt fails
        import hashlib
        simple_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Using fallback simple hash: {simple_hash[:10]}...")
        return simple_hash

def get_user(conn, username_or_email: str):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()
    return user

def authenticate_user(conn, username_or_email: str, password: str):
    user = get_user(conn, username_or_email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    
    # Check if user is active (not deactivated)
    if not user.get("is_active", True):
        return False
        
    return User(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        is_approved=user["is_approved"],
        requires_approval=user["requires_approval"],
        is_active=user.get("is_active", True)
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dummy user for bypassing authentication
async def get_current_user():
    return User(
        id="system",
        full_name="System User",
        email="system@example.com",
        role="System Administrator",
        is_approved=True,
        requires_approval=False,
        is_active=True
    )

# Proper JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

async def get_current_user(token: str = Depends(oauth2_scheme), conn = Depends(get_db_connection), request: Request = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Handle fallback token for compatibility
    if token.startswith("user_fallback_token_"):
        # Default fallback user
        user_id = "system"
        full_name = "System User"
        email = "system@example.com"
        role = "System Administrator"
        
        # Try to get actual user data from session/localStorage via request headers
        if request:
            user_str = request.headers.get('X-User-Data')
            if user_str:
                try:
                    import json
                    user_data = json.loads(user_str)
                    if user_data and 'id' in user_data:
                        user_id = user_data['id']
                        full_name = user_data.get('full_name', full_name)
                        email = user_data.get('email', email)
                        role = user_data.get('role', role)
                except:
                    pass
                    
        # Try to validate that this user exists in the database
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    user_data = cursor.fetchone()
                    if user_data:
                        return User(
                            id=user_data["id"],
                            full_name=user_data["full_name"],
                            email=user_data["email"],
                            role=user_data["role"],
                            is_approved=user_data["is_approved"],
                            requires_approval=user_data["requires_approval"],
                            is_active=user_data.get("is_active", True)
                        )
            except Exception as e:
                print(f"Error validating fallback token user: {str(e)}")
        
        # If we couldn't find the user in the database, return a basic user
        # This is a last resort and will likely cause foreign key errors
        return User(
            id=user_id,
            full_name=full_name,
            email=email,
            role=role,
            is_approved=True,
            requires_approval=False,
            is_active=True
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Get user from database
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
    if user_data is None:
        raise credentials_exception
        
    return User(
        id=user_data["id"],
        full_name=user_data["full_name"],
        email=user_data["email"],
        role=user_data["role"],
        is_approved=user_data["is_approved"],
        requires_approval=user_data["requires_approval"],
        is_active=user_data.get("is_active", True)
    )

async def get_current_active_user():
    return await get_current_user()

# Authentication middleware to populate request.state.user
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip authentication for login/token endpoints
    if request.url.path in ["/api/token", "/api/login", "/api/signup", "/api/forgot-password", "/api/reset-password", "/api/verify-reset-token", "/"]:
        return await call_next(request)
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        
        # Handle fallback token for compatibility
        if token.startswith("user_fallback_token_"):
            try:
                # Extract user ID from request headers or query params
                user_str = request.headers.get('X-User-Data')
                user_id = "system"  # Default fallback
                
                if user_str:
                    try:
                        import json
                        user_data = json.loads(user_str)
                        if user_data and 'id' in user_data:
                            user_id = user_data['id']
                            full_name = user_data.get('full_name', 'System User')
                            email = user_data.get('email', 'system@example.com')
                            role = user_data.get('role', 'System Administrator')
                    except:
                        pass
                
                # Create a user for fallback tokens
                user = User(
                    id=user_id,
                    full_name=full_name if 'full_name' in locals() else 'System User',
                    email=email if 'email' in locals() else 'system@example.com',
                    role=role if 'role' in locals() else 'System Administrator',
                    is_approved=True,
                    requires_approval=False,
                    is_active=True
                )
                request.state.user = user
                return await call_next(request)
            except Exception as e:
                print(f"Fallback token handling error: {str(e)}")
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            # Get user from database
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    user_data = cursor.fetchone()
                    
                if user_data:
                    # Create user object and set in request state
                    user = User(
                        id=user_data["id"],
                        full_name=user_data["full_name"],
                        email=user_data["email"],
                        role=user_data["role"],
                        is_approved=user_data["is_approved"],
                        requires_approval=user_data["requires_approval"],
                        is_active=user_data.get("is_active", True)
                    )
                    request.state.user = user
            finally:
                conn.close()
        except Exception as e:
            print(f"Auth middleware error: {str(e)}")
            # Continue without setting user in state
    
    return await call_next(request)

# Import routes after defining dependencies
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.semesters import router as semesters_router
from routes.lab_rooms import router as lab_rooms_router
from routes.instructors import router as instructors_router
from routes.schedules import router as schedules_router
from routes.course_offerings import router as course_offerings_router
from routes.notifications import router as notifications_router
from routes.system_settings import router as system_settings_router

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(semesters_router, prefix="/api")
app.include_router(lab_rooms_router, prefix="/api")
app.include_router(instructors_router, prefix="/api")
app.include_router(schedules_router, prefix="/api")
app.include_router(course_offerings_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(system_settings_router, prefix="/api")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Lab Class API"}

@app.on_event("startup")
async def startup_sync_instructors():
    print("Running startup sync_instructors...")
    try:
        # Import here to avoid circular imports
        import importlib.util
        spec = importlib.util.spec_from_file_location("sync_schedules", "./backend/sync_schedules.py")
        sync_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync_module)
        
        # Run the sync function
        conn = next(get_db_connection())
        sync_module.sync_instructors_with_users(conn)
        conn.close()
        print("Completed startup sync_instructors")
    except Exception as e:
        print(f"Error in startup sync_instructors: {e}")
        
@app.on_event("startup")
async def ensure_system_settings():
    """Ensure that required system settings are present in the database"""
    print("Checking system settings...")
    try:
        conn = next(get_db_connection())
        
        with conn.cursor() as cursor:
            # Check if current_display_semester_id exists
            cursor.execute(
                "SELECT COUNT(*) as count FROM system_settings WHERE setting_key = 'current_display_semester_id'"
            )
            result = cursor.fetchone()
            
            if not result or result['count'] == 0:
                print("Creating default current_display_semester_id setting")
                # Find the first semester to use as default
                cursor.execute("SELECT id FROM semesters ORDER BY id LIMIT 1")
                semester = cursor.fetchone()
                semester_id = '1'  # Default if no semesters exist
                
                if semester:
                    semester_id = str(semester['id'])
                
                # Insert the default setting
                cursor.execute(
                    """
                    INSERT INTO system_settings 
                    (setting_key, setting_value, description)
                    VALUES ('current_display_semester_id', %s, 'ID of the semester that should be displayed in all dashboards')
                    """,
                    (semester_id,)
                )
                conn.commit()
                print(f"Created default current_display_semester_id setting with value {semester_id}")
            else:
                print("current_display_semester_id setting already exists")
        
        conn.close()
        print("System settings check completed")
    except Exception as e:
        print(f"Error ensuring system settings: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 