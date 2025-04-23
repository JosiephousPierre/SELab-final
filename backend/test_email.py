import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test email
def send_approval_email(email, name, role):
    """Helper function to send an account approval notification email."""
    # Hard-coded email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = "587"
    smtp_username = "pierredosdos@gmail.com"
    smtp_password = "bzos rzhj ptew lure"
    
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
        
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.set_debuglevel(1)  # Enable debug output
            print("Starting TLS...")
            server.starttls()
            print(f"Logging in with username: {smtp_username}")
            server.login(smtp_username, smtp_password)
            print(f"Sending mail from {smtp_username} to {email}")
            server.sendmail(smtp_username, email, message.as_string())
        
        print(f"Account approval email sent to {email}")
        return True
    except Exception as e:
        print(f"Error sending approval email: {str(e)}")
        # Don't raise the exception here, just log it
        import traceback
        traceback.print_exc()
        return False

# Run the test
print("Testing send_approval_email function...")
recipient_email = "youremail@example.com"  # Replace with your email for testing
test_name = "Test User"
test_role = "Faculty/Staff"

result = send_approval_email(recipient_email, test_name, test_role)
if result:
    print("Test completed successfully!")
else:
    print("Test failed!") 