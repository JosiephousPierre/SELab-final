from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os
import pymysql
import traceback
import ssl

# Import from main app - update to absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import (
    get_db_connection,
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    get_current_user
)

router = APIRouter(tags=["authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    full_name: str
    email: str
    role: str
    requires_approval: bool
    is_approved: bool
    is_active: bool

class UserSignUp(BaseModel):
    id: str
    full_name: str
    email: str
    password: str
    role: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn = Depends(get_db_connection)
):
    print(f"LOGIN ATTEMPT: Username: {form_data.username}")
    
    # First, check if user exists in the database
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (form_data.username, form_data.username)
        )
        db_user = cursor.fetchone()
    
    if db_user:
        print(f"User found in DB: {db_user['id']}, {db_user['email']}")
        print(f"User status: is_approved={db_user.get('is_approved', 'Not set')}, requires_approval={db_user.get('requires_approval', 'Not set')}, is_active={db_user.get('is_active', 'Not set')}")
    else:
        print(f"User not found in database: {form_data.username}")
    
    user = authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        print(f"Authentication failed: Incorrect username or password for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Authentication successful for {user.id}, checking approval status")
    print(f"User status after auth: is_approved={user.is_approved}, requires_approval={user.requires_approval}, is_active={user.is_active}")
    
    # If the user requires approval and is not approved yet
    if user.requires_approval and not user.is_approved:
        print(f"APPROVAL FAILURE: User {user.id} requires approval but is not approved yet")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval by an administrator",
        )
    
    # If the user account has been deactivated
    if not user.is_active:
        print(f"ACTIVATION FAILURE: User {user.id} account is deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )
    
    # All checks passed, generate token
    print(f"All checks PASSED for {user.id}, generating token")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "requires_approval": user.requires_approval,
        "is_approved": user.is_approved,
        "is_active": user.is_active
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp, request: Request, conn = Depends(get_db_connection)):
    # Check if user with this ID or email already exists
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s",
            (user_data.id, user_data.email)
        )
        existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this ID or email already exists"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Determine if user requires approval based on role
    requires_approval = True
    is_approved = False
    
    # Students don't require approval
    if user_data.role.lower() == 'student':
        requires_approval = False
        is_approved = True
    
    # Insert new user
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users 
                (id, full_name, email, password, role, is_approved, requires_approval, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_data.id,
                    user_data.full_name,
                    user_data.email,
                    hashed_password,
                    user_data.role,
                    is_approved,
                    requires_approval,
                    True  # Set is_active to True for all new users
                )
            )
            
            # Log the signup event
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_data.id,
                    "SIGNUP",
                    f"User signed up with role: {user_data.role}", 
                    client_ip
                )
            )
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
    
    return {
        "message": "User registered successfully",
        "requires_approval": requires_approval,
        "is_approved": is_approved
    }

class LoginRequest(BaseModel):
    id_or_email: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    conn = Depends(get_db_connection)
):
    print(f"LOGIN ATTEMPT via /login endpoint: Username: {login_data.id_or_email}")
    
    # First, check if user exists in the database
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (login_data.id_or_email, login_data.id_or_email)
        )
        db_user = cursor.fetchone()
    
    if db_user:
        print(f"User found in DB: {db_user['id']}, {db_user['email']}")
        print(f"User status: is_approved={db_user.get('is_approved', 'Not set')}, requires_approval={db_user.get('requires_approval', 'Not set')}, is_active={db_user.get('is_active', 'Not set')}")
    else:
        print(f"User not found in database: {login_data.id_or_email}")
    
    user = authenticate_user(conn, login_data.id_or_email, login_data.password)
    if not user:
        print(f"Authentication failed: Incorrect username or password for {login_data.id_or_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Authentication successful for {user.id}, checking approval status")
    print(f"User status after auth: is_approved={user.is_approved}, requires_approval={user.requires_approval}, is_active={user.is_active}")
    
    # If the user requires approval and is not approved yet
    if user.requires_approval and not user.is_approved:
        print(f"APPROVAL FAILURE: User {user.id} requires approval but is not approved yet")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval by an administrator",
        )
    
    # If the user account has been deactivated
    if not user.is_active:
        print(f"ACTIVATION FAILURE: User {user.id} account is deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )
    
    # All checks passed, generate token
    print(f"All checks PASSED for {user.id}, generating token")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "requires_approval": user.requires_approval,
        "is_approved": user.is_approved,
        "is_active": user.is_active
    }

# Add the password reset request class
class PasswordResetRequest(BaseModel):
    email: str

class VerifyTokenRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Add the forgot password endpoint
@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    request_data: PasswordResetRequest,
    request_obj: Request,
    conn = Depends(get_db_connection)
):
    """
    Send a password reset email to the user.
    For this demo, we'll simulate sending an email and return success even if the email is not found.
    This is a security best practice to prevent email enumeration attacks.
    """
    # Add CORS headers for this specific endpoint
    origin = request_obj.headers.get("origin", "http://localhost:5173")
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    
    try:
        # Check if the email exists in the database
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (request_data.email,)
            )
            user = cursor.fetchone()
        
        # Generate a reset token, whether or not the user exists
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        if user:
            try:
                # Store the reset token in the database
                with conn.cursor() as cursor:
                    # Check if a reset token already exists for this user
                    cursor.execute(
                        "SELECT * FROM password_reset_tokens WHERE user_id = %s",
                        (user["id"],)
                    )
                    existing_token = cursor.fetchone()
                    
                    if existing_token:
                        # Update the existing token
                        cursor.execute(
                            """
                            UPDATE password_reset_tokens 
                            SET token = %s, expires_at = %s, created_at = %s
                            WHERE user_id = %s
                            """,
                            (
                                reset_token,
                                reset_token_expiry.isoformat(),
                                datetime.utcnow().isoformat(),
                                user["id"]
                            )
                        )
                    else:
                        # Create a new token
                        cursor.execute(
                            """
                            INSERT INTO password_reset_tokens 
                            (user_id, token, expires_at, created_at) 
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                user["id"],
                                reset_token,
                                reset_token_expiry.isoformat(),
                                datetime.utcnow().isoformat()
                            )
                        )
                    conn.commit()
                
                # In a real application, send an email here
                # For demo purposes, we'll log what would be sent
                reset_url = f"http://localhost:5173/reset-password?token={reset_token}&email={request_data.email}"
                print(f"[MOCK EMAIL] Password reset link for {request_data.email}: {reset_url}")
                
                # Send reset email with handling timeouts and errors
                try:
                    send_reset_email(request_data.email, reset_url, user["full_name"])
                except Exception as email_error:
                    print(f"Error sending reset email: {str(email_error)}")
                    # Don't fail the request just because email sending failed
            except Exception as db_error:
                print(f"Database error in forgot_password: {str(db_error)}")
                conn.rollback()
                # Continue to return success response even if DB operation failed
        
        # Always return success to prevent email enumeration
        return JSONResponse(
            content={
                "message": "If the email exists in our system, a password reset link will be sent.",
                "success": True
            },
            headers=headers
        )
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        return JSONResponse(
            content={
                "message": "If the email exists in our system, a password reset link will be sent.",
                "success": True
            },
            headers=headers
        )

def send_reset_email(email, reset_url, name):
    """Helper function to send a password reset email."""
    # Hard-coded email configuration (same as send_approval_email)
    smtp_server = "smtp.gmail.com"
    smtp_port = "587"
    smtp_username = "pierredosdos@gmail.com"
    smtp_password = "bibb iylk bqkc grez"
    
    try:
        # For development/demo environment, just log and return success
        # This prevents timeouts during development
        if os.environ.get("FLASK_ENV") == "development" or os.environ.get("DEBUG") == "1":
            print(f"[DEV MODE] Would send password reset email to {email} with URL: {reset_url}")
            return True
            
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request"
        message["From"] = smtp_username
        message["To"] = email
        
        # Plain text version - simplified for faster sending
        text = f"""
Hello {name},

You recently requested to reset your password. Click the link below to reset it:

{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
The UIC Lab Class Scheduler Team
        """
        
        # HTML version - simplified for faster sending
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #DD385A; color: white; padding: 10px 20px; text-align: center;">
            <h2>Password Reset Request</h2>
        </div>
        <div style="padding: 20px;">
            <p>Hello {name},</p>
            <p>You recently requested to reset your password. Click the button below to reset it:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" style="display: inline-block; background-color: #DD385A; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{reset_url}</p>
            <p>This link will expire in 1 hour.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <div style="margin-top: 30px; font-size: 12px; color: #777;">
                <p>Best regards,<br>The UIC Lab Class Scheduler Team</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email with timeout
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, int(smtp_port), timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, email, message.as_string())
        
        print(f"Password reset email sent to {email}")
        return True
    except smtplib.SMTPException as e:
        print(f"SMTP Error sending reset email: {str(e)}")
        # Don't raise the exception here, just log it
        return False
    except Exception as e:
        print(f"Error sending reset email: {str(e)}")
        # Don't raise the exception here, just log it
        return False

def send_approval_email(email, name, role):
    """Helper function to send an account approval notification email."""
    # Hard-coded email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = "587"
    smtp_username = "pierredosdos@gmail.com"
    smtp_password = "bibb iylk bqkc grez"
    
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Account Has Been Approved"
        message["From"] = smtp_username
        message["To"] = email
        
        # Login URL
        login_url = "http://localhost:5173/login"
        
        # Plain text version
        text = f"""
        Hello {name},
        
        Great news! Your account has been approved with the role of {role}.
        
        You can now log in to the UIC Lab Class Scheduler using the following link:
        
        {login_url}
        
        If you have any questions or need assistance, please contact the system administrator.
        
        Best regards,
        The UIC Lab Class Scheduler Team
        """
        
        # HTML version
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #DD385A; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ display: inline-block; background-color: #DD385A; color: white; 
                          padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Account Approved!</h2>
                </div>
                <div class="content">
                    <p>Hello {name},</p>
                    <p>Great news! Your account has been approved with the role of <strong>{role}</strong>.</p>
                    <p>You can now log in to the UIC Lab Class Scheduler using the button below:</p>
                    <p style="text-align: center;">
                        <a href="{login_url}" class="button">Log In Now</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p>{login_url}</p>
                    <p>If you have any questions or need assistance, please contact the system administrator.</p>
                    <div class="footer">
                        <p>Best regards,<br>The UIC Lab Class Scheduler Team</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, email, message.as_string())
        
        print(f"Account approval email sent to {email}")
    except Exception as e:
        print(f"Error sending approval email: {str(e)}")
        # Don't raise the exception here, just log it
        # This ensures the approval process continues even if email sending fails

@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyTokenRequest):
    # Add CORS headers for this specific endpoint
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Verify token request received: {request.token[:10]}...")
    
    if not request.token or len(request.token) < 10:
        print(f"Token validation failed: Token too short or missing")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid token format"},
            headers=headers
        )
    
    try:
        # Check if token exists and is not expired
        cursor.execute("""
            SELECT user_id, expires_at FROM password_reset_tokens 
            WHERE token = %s AND expires_at > NOW()
        """, (request.token,))
        
        result = cursor.fetchone()
        
        if not result:
            # Token doesn't exist or is expired
            print(f"Token not found in database or expired: {request.token[:10]}...")
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid or expired token"},
                headers=headers
            )
        
        # Token is valid
        print(f"Token validated successfully for user: {result['user_id']}")
        return JSONResponse(
            content={"valid": True, "user_id": result['user_id']},
            headers=headers,
            status_code=200
        )
    except Exception as e:
        print(f"Error verifying token: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred while verifying the token: {str(e)}"},
            headers=headers
        )
    finally:
        cursor.close()
        conn.close()

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset a user's password using a valid token"""
    # Connect to the database
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="labclass_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    try:
        # Detailed request logging
        print(f"Password reset request received for token: {request.token[:10]}...")
        
        if not request.token or len(request.token) < 10:
            print(f"Token validation failed: Token too short or missing")
            return {"detail": "Invalid token format"}
        
        if not request.new_password:
            print(f"Password reset failed: New password is empty")
            return {"detail": "New password cannot be empty"}
        
        # Check if token exists in the database
        cursor.execute("""
            SELECT user_id, expires_at FROM password_reset_tokens 
            WHERE token = %s
        """, (request.token,))
        
        result = cursor.fetchone()
        
        if not result:
            # Token doesn't exist
            print(f"Token not found in database: {request.token[:10]}...")
            return {"detail": "Invalid token - not found in database"}
                
        # Check if token is expired
        current_time = datetime.now()
        expires_at = result['expires_at']
        
        # Convert to string for comparison if needed
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        print(f"Token expires at: {expires_at}, current time: {current_time}")
        
        if expires_at < current_time:
            print(f"Token expired: {request.token[:10]}...")
            return {"detail": "Expired token - please request a new password reset"}
        
        # Get user ID
        user_id = result['user_id']
        print(f"Valid token found for user_id: {user_id}")
        
        # Get user details for a more personalized response
        cursor.execute("SELECT full_name, email FROM users WHERE id = %s", (user_id,))
        user_details = cursor.fetchone()
        
        if not user_details:
            print(f"User not found for ID: {user_id}")
            return {"detail": "User not found - cannot reset password"}
        
        # Hash the new password
        hashed_password = get_password_hash(request.new_password)
        print(f"New password hashed successfully")
        
        # Update the user's password - EXPLICITLY COMMIT THIS CHANGE
        try:
            cursor.execute("""
                UPDATE users SET password = %s WHERE id = %s
            """, (hashed_password, user_id))
            
            # Verify the update was successful
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            
            if not updated_user or updated_user['password'] != hashed_password:
                print(f"Password update verification failed for user_id: {user_id}")
                conn.rollback()
                return {"detail": "Failed to update password - verification failed"}
            
            print(f"Password updated successfully for user_id: {user_id}")
            
            # Delete all password reset tokens for this user
            cursor.execute("""
                DELETE FROM password_reset_tokens WHERE user_id = %s
            """, (user_id,))
            
            print(f"Reset tokens deleted for user_id: {user_id}")
            
            # Commit the changes
            conn.commit()
            print(f"Database changes committed successfully")
        except Exception as db_error:
            print(f"Database error updating password: {db_error}")
            conn.rollback()
            return {"detail": f"Database error: {str(db_error)}"}
        
        return {
            "message": "Password reset successfully", 
            "success": True,
            "user_id": user_id,
            "full_name": user_details.get('full_name') if user_details else None,
            "email": user_details.get('email') if user_details else None
        }
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error resetting password: {e}")
        traceback.print_exc()
        return {"detail": f"An error occurred while resetting the password: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.options("/verify-reset-token", include_in_schema=False)
async def options_verify_reset_token():
    """Handle preflight CORS for verify-reset-token"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    return JSONResponse(content={"status": "ok"}, headers=headers)

@router.options("/forgot-password", include_in_schema=False)
async def options_forgot_password(request: Request):
    """Handle preflight CORS for forgot-password"""
    origin = request.headers.get("origin", "http://localhost:5173")
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    return JSONResponse(content={"status": "ok"}, headers=headers)

@router.get("/auth-health-check")
async def auth_health_check():
    """Simple health check endpoint to test if the auth router is responding."""
    return {"status": "ok", "message": "Auth router is functioning correctly"}

@router.get("/password-reset-debug")
async def password_reset_debug():
    """Debug endpoint to confirm the API server is accessible and handling password reset routes."""
    print("Debug endpoint accessed")
    return {
        "status": "ok", 
        "message": "Password reset debug endpoint is working", 
        "timestamp": datetime.now().isoformat()
    }

class TestPasswordResetRequest(BaseModel):
    email: str = "test@example.com"
    new_password: str = "testpassword123"

@router.post("/test-password-reset")
async def test_password_reset(request: TestPasswordResetRequest, request_obj: Request):
    """Test endpoint to reset a password without requiring a token (for debugging only)"""
    email = request.email
    new_password = request.new_password
    print(f"Test password reset for email: {email}")
    
    # Add CORS headers for this specific endpoint
    origin = request_obj.headers.get("origin", "http://localhost:5173")
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    
    try:
        # Connect to the database - create the connection directly
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="labclass_db",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Find user by email
        cursor.execute("SELECT id, email, full_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"User not found with email: {email}")
            return JSONResponse(
                content={"message": "Test password reset - user not found", "email": email},
                headers=headers
            )
        
        # Get user ID
        user_id = user['id']
        
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        
        # Update the user's password - explicitly commit this change
        try:
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                          (hashed_password, user_id))
            
            # Verify the update was successful
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            
            if not updated_user or updated_user['password'] != hashed_password:
                print(f"Password update verification failed for user_id: {user_id}")
                conn.rollback()
                return JSONResponse(
                    content={"detail": "Failed to update password - verification failed"},
                    headers=headers,
                    status_code=500
                )
            
            print(f"Password updated successfully for user_id: {user_id}")
            
            # Commit the changes
            conn.commit()
        except Exception as db_error:
            print(f"Database error updating password: {db_error}")
            conn.rollback()
            return JSONResponse(
                content={"detail": f"Database error: {str(db_error)}"},
                headers=headers,
                status_code=500
            )
        
        return JSONResponse(
            content={
                "message": "Test password reset successful",
                "email": email,
                "user_id": user_id,
                "full_name": user.get('full_name', 'User')
            },
            headers=headers,
            status_code=200
        )
    except Exception as e:
        print(f"Error in test password reset: {str(e)}")
        traceback.print_exc()
        if 'conn' in locals() and conn:
            conn.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error in test password reset: {str(e)}"},
            headers=headers
        )
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@router.options("/test-password-reset", include_in_schema=False)
async def options_test_password_reset(request: Request):
    """Handle preflight CORS for test-password-reset"""
    origin = request.headers.get("origin", "http://localhost:5173")
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }
    return JSONResponse(content={"status": "ok"}, headers=headers) 