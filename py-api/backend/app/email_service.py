"""
Email service for sending activation and password reset emails
"""
import smtplib
import os
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from .database import settings


async def send_activation_email(email: str, activation_token: str, user_name: str) -> bool:
    """Send account activation email"""
    try:
        print(f"[EMAIL] Attempting to send activation email to: {email}")
        
        # Validate email configuration
        if not settings.smtp_host or settings.smtp_host.strip() == "":
            print("[EMAIL ERROR] SMTP_HOST not configured in Railway environment variables")
            print("[EMAIL ERROR] Please set SMTP_HOST=smtp.gmail.com in Railway Variables")
            return False
        
        if not settings.smtp_user or settings.smtp_user == "your-email@gmail.com" or settings.smtp_user.strip() == "":
            print("[EMAIL ERROR] SMTP_USER not configured in Railway environment variables")
            print("[EMAIL ERROR] Please set SMTP_USER=zenvia07@gmail.com in Railway Variables")
            return False
        
        if not settings.smtp_password or settings.smtp_password == "your-app-password" or settings.smtp_password.strip() == "":
            print("[EMAIL ERROR] SMTP_PASSWORD not configured in Railway environment variables")
            print("[EMAIL ERROR] Please set SMTP_PASSWORD=ogntznelsmhkqdvi in Railway Variables")
            return False
        
        # Ensure recipient is different from sender
        if email.lower() == settings.email_from.lower():
            print(f"[EMAIL ERROR] Recipient cannot be the same as sender!")
            return False
        
        # Create activation URL
        base_url = os.getenv("FRONTEND_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        
        if not base_url:
            railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
            if railway_url:
                base_url = f"https://{railway_url}"
            else:
                base_url = "http://localhost:3000"
        
        if base_url and not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        
        activation_url = f"{base_url}/?token={activation_token}"
        print(f"[EMAIL] Activation URL: {activation_url}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Activate Your Account - Login API"
        
        # Format sender with display name to hide email address
        if '<' in settings.email_from and '>' in settings.email_from:
            msg['From'] = settings.email_from
        else:
            msg['From'] = f"Login App <{settings.email_from}>"
        
        msg['To'] = email
        
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
        
        # Send email with retry logic
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                smtp_host = settings.smtp_host.strip()
                smtp_port = settings.smtp_port
                print(f"[EMAIL] Attempt {attempt + 1}/{max_retries}: Connecting to SMTP server: {smtp_host}:{smtp_port}")
                
                if not smtp_host:
                    print("[EMAIL ERROR] SMTP_HOST is empty! Please set it in Railway Variables")
                    return False
                
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                print(f"[EMAIL] Connected to SMTP server")
                server.starttls()
                print(f"[EMAIL] TLS started")
                print(f"[EMAIL] Logging in as: {settings.smtp_user}")
                server.login(settings.smtp_user, settings.smtp_password)
                print(f"[EMAIL] Login successful")
                print(f"[EMAIL] Sending email to: {email}")
                server.send_message(msg)
                server.quit()
                print(f"[EMAIL SUCCESS] Activation email sent successfully to {email}")
                return True
                
            except OSError as e:
                error_msg = str(e)
                if ("Network is unreachable" in error_msg or "101" in error_msg) and attempt < max_retries - 1:
                    print(f"[EMAIL] Network error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    print(f"[EMAIL ERROR] SMTP network error: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                    
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
        import os
        base_url = os.getenv("FRONTEND_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or "http://localhost:3000"
        if base_url and not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        
        reset_url = f"{base_url}/reset-password?token={reset_token}"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Reset Your Password"
        
        # Format sender with display name
        if '<' in settings.email_from and '>' in settings.email_from:
            msg['From'] = settings.email_from
        else:
            msg['From'] = f"Login App <{settings.email_from}>"
        
        msg['To'] = email
        
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
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #6366f1;">Hello {user_name},</h2>
              <p>You requested to reset your password. Click the button below to reset it:</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #6366f1; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 8px; display: inline-block;">
                  Reset Password
                </a>
              </div>
              <p>Or copy and paste this link:</p>
              <p style="word-break: break-all; color: #666;">{reset_url}</p>
              <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
              <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
            </div>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email with retry logic
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
                print(f"[EMAIL SUCCESS] Password reset email sent successfully to {email}")
                return True
                
            except OSError as e:
                if ("Network is unreachable" in str(e) or "101" in str(e)) and attempt < max_retries - 1:
                    print(f"[EMAIL] Network error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    print(f"[EMAIL ERROR] SMTP error: {e}")
                    return False
            except Exception as e:
                print(f"[EMAIL ERROR] Error sending password reset email: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return False
        
        return False
        
    except Exception as e:
        print(f"[EMAIL ERROR] Error sending password reset email: {e}")
        import traceback
        traceback.print_exc()
        return False
