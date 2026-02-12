"""
Email service for sending activation and password reset emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from .database import settings


async def send_activation_email(email: str, activation_token: str, user_name: str) -> bool:
    """Send account activation email"""
    try:
        print(f"[EMAIL] Attempting to send activation email to: {email}")
        
        # Validate email configuration
        if not settings.smtp_user or settings.smtp_user == "your-email@gmail.com":
            print("[EMAIL ERROR] SMTP user not configured in .env file")
            return False
        
        if not settings.smtp_password or settings.smtp_password == "your-app-password":
            print("[EMAIL ERROR] SMTP password not configured in .env file")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Activate Your Account - Login API"
        
        # Format sender with display name to hide email address
        # If EMAIL_FROM already has a display name, use it; otherwise add one
        if '<' in settings.email_from and '>' in settings.email_from:
            # Already in format "Name <email@domain.com>"
            msg['From'] = settings.email_from
        else:
            # Add display name to hide the actual email address
            msg['From'] = f"Login App <{settings.email_from}>"
        
        msg['To'] = email  # Recipient: the user who registered (e.g., akarshachinta@gmail.com)
        
        # Verify we're sending to the correct email (not the sender's email)
        print(f"[EMAIL] Email FROM (sender): {settings.email_from}")
        print(f"[EMAIL] Email TO (recipient): {email}")
        
        if email == settings.email_from:
            print(f"[EMAIL ERROR] WARNING: Recipient email matches sender email! This might be wrong.")
        
        # Ensure recipient is different from sender
        if email.lower() == settings.email_from.lower():
            print(f"[EMAIL ERROR] Recipient cannot be the same as sender!")
            return False
        
        # Create activation URL
        # Get the base URL from environment or detect from Railway
        import os
        # Check for Railway's public domain or custom FRONTEND_URL
        base_url = os.getenv("FRONTEND_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        
        # If still not set, try to detect from Railway environment
        if not base_url:
            # Railway sets RAILWAY_PUBLIC_DOMAIN, but if not available, use a default
            # For Railway deployments, the frontend and backend are on the same domain
            railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
            if railway_url:
                base_url = f"https://{railway_url}"
            else:
                # Fallback: use localhost for local development
                base_url = "http://localhost:3000"
        
        # Ensure URL has protocol
        if base_url and not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        
        # Use root path with token parameter - frontend will detect and handle it
        activation_url = f"{base_url}/?token={activation_token}"
        print(f"[EMAIL] Activation URL: {activation_url}")
        
        # Email body
        text = f"""
Hello {user_name},

Thank you for registering with our service! 

Please activate your account by clicking the link below:

{activation_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Login API Team
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #6366f1;">Hello {user_name},</h2>
              <p>Thank you for registering with our service!</p>
              <p>Please activate your account by clicking the button below:</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{activation_url}" 
                   style="background-color: #6366f1; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 8px; display: inline-block;">
                  Activate Account
                </a>
              </div>
              <p>Or copy and paste this link into your browser:</p>
              <p style="word-break: break-all; color: #666;">{activation_url}</p>
              <p style="color: #999; font-size: 12px;">This link will expire in 24 hours.</p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
              <p style="color: #999; font-size: 12px;">
                If you didn't create this account, please ignore this email.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        print(f"[EMAIL] Connecting to SMTP server: {settings.smtp_host}:{settings.smtp_port}")
        print(f"[EMAIL] SMTP_USER: {settings.smtp_user}")
        print(f"[EMAIL] SMTP_PASSWORD length: {len(settings.smtp_password) if settings.smtp_password else 0} characters")
        print(f"[EMAIL] EMAIL_FROM: {settings.email_from}")
        
        try:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
            print(f"[EMAIL] Connected to SMTP server")
            server.starttls()
            print(f"[EMAIL] TLS started")
            print(f"[EMAIL] Attempting login as: {settings.smtp_user}")
            server.login(settings.smtp_user, settings.smtp_password)
            print(f"[EMAIL] Login successful")
            print(f"[EMAIL] Sending email to: {email}")
            server.send_message(msg)
            server.quit()
            print(f"[EMAIL SUCCESS] Activation email sent successfully to {email}")
            return True
        except Exception as smtp_error:
            print(f"[EMAIL ERROR] SMTP operation failed: {type(smtp_error).__name__}: {smtp_error}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise to be caught by outer exception handler
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"[EMAIL ERROR] SMTP Authentication failed: {e}"
        print(error_msg)
        print("[EMAIL ERROR] Please check your email and app password in Railway environment variables")
        print(f"[EMAIL ERROR] SMTP_USER: {settings.smtp_user}")
        print(f"[EMAIL ERROR] SMTP_PASSWORD length: {len(settings.smtp_password) if settings.smtp_password else 0} characters")
        import traceback
        traceback.print_exc()
        return False
    except smtplib.SMTPException as e:
        error_msg = f"[EMAIL ERROR] SMTP error: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        error_msg = f"[EMAIL ERROR] Error sending activation email: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False


async def send_password_reset_email(email: str, reset_token: str, user_name: str) -> bool:
    """Send password reset email"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Reset Your Password"
        
        # Format sender with display name to hide email address
        # If EMAIL_FROM already has a display name, use it; otherwise add one
        if '<' in settings.email_from and '>' in settings.email_from:
            # Already in format "Name <email@domain.com>"
            msg['From'] = settings.email_from
        else:
            # Add display name to hide the actual email address
            msg['From'] = f"Login App <{settings.email_from}>"
        
        msg['To'] = email
        
        # Create reset URL (adjust based on your frontend URL)
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # Email body
        text = f"""
        Hello {user_name},
        
        You requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email and your password will remain unchanged.
        """
        
        html = f"""
        <html>
          <body>
            <h2>Hello {user_name},</h2>
            <p>You requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
