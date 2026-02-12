"""
Email service for sending activation and password reset emails
Supports both SMTP (for local dev) and SendGrid API (for Railway)
"""
import smtplib
import os
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from .database import settings
import httpx


async def send_email_via_sendgrid(email: str, subject: str, text_content: str, html_content: str, user_name: str) -> bool:
    """Send email using SendGrid API (works on Railway)"""
    try:
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not sendgrid_api_key:
            print("[EMAIL] SENDGRID_API_KEY not set, cannot use SendGrid")
            return False
        
        sendgrid_url = "https://api.sendgrid.com/v3/mail/send"
        
        # Format sender email
        from_email = settings.email_from
        if '<' in from_email and '>' in from_email:
            # Extract email from "Name <email@domain.com>" format
            from_email = from_email.split('<')[1].split('>')[0].strip()
        
        payload = {
            "personalizations": [{
                "to": [{"email": email, "name": user_name}],
                "subject": subject
            }],
            "from": {
                "email": from_email,
                "name": "Login App"
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": text_content
                },
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"[EMAIL] Sending via SendGrid API to: {email}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(sendgrid_url, json=payload, headers=headers)
            
            if response.status_code == 202:
                print(f"[EMAIL SUCCESS] Email sent via SendGrid to {email}")
                return True
            else:
                print(f"[EMAIL ERROR] SendGrid API error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"[EMAIL ERROR] SendGrid API exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def send_email_via_smtp(email: str, subject: str, text_content: str, html_content: str, user_name: str) -> bool:
    """Send email using SMTP (with retry logic for Railway network issues)"""
    import time
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            
            # Format sender with display name
            if '<' in settings.email_from and '>' in settings.email_from:
                msg['From'] = settings.email_from
            else:
                msg['From'] = f"Login App <{settings.email_from}>"
            
            msg['To'] = email
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email with retry
            print(f"[EMAIL] Attempt {attempt + 1}/{max_retries}: Connecting to SMTP server: {settings.smtp_host}:{settings.smtp_port}")
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"[EMAIL SUCCESS] Email sent via SMTP to {email}")
            return True
            
        except OSError as e:
            # Network unreachable or connection errors
            error_msg = str(e)
            if "Network is unreachable" in error_msg or "101" in error_msg:
                if attempt < max_retries - 1:
                    print(f"[EMAIL] Network error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"[EMAIL ERROR] SMTP network unreachable after {max_retries} attempts. Railway may be blocking SMTP.")
                    print(f"[EMAIL] Consider using SendGrid API instead (set SENDGRID_API_KEY)")
                    return False
            else:
                print(f"[EMAIL ERROR] SMTP OSError: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"[EMAIL ERROR] SMTP error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False


async def send_activation_email(email: str, activation_token: str, user_name: str) -> bool:
    """Send account activation email"""
    try:
        print(f"[EMAIL] Attempting to send activation email to: {email}")
        
        # Ensure recipient is different from sender
        if email.lower() == settings.email_from.lower():
            print(f"[EMAIL ERROR] Recipient cannot be the same as sender!")
            return False
        
        # Create activation URL
        import os
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
        
        # Email content
        subject = "Activate Your Account - Login API"
        text_content = f"""
Hello {user_name},

Thank you for registering with our service! 

Please activate your account by clicking the link below:

{activation_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Login API Team
        """
        
        html_content = f"""
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
        
        # Try SendGrid API first if available (works reliably on Railway)
        # Otherwise try SMTP with retry logic
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_key:
            print("[EMAIL] Using SendGrid API (Railway compatible)")
            result = await send_email_via_sendgrid(email, subject, text_content, html_content, user_name)
            if result:
                return True
            print("[EMAIL] SendGrid failed, falling back to SMTP...")
        
        # Try SMTP (may work intermittently on Railway)
        print("[EMAIL] Attempting SMTP connection...")
        # Validate SMTP configuration
        if not settings.smtp_user or settings.smtp_user == "your-email@gmail.com":
            print("[EMAIL ERROR] SMTP user not configured")
            return False
        
        if not settings.smtp_password or settings.smtp_password == "your-app-password":
            print("[EMAIL ERROR] SMTP password not configured")
            return False
        
        return await send_email_via_smtp(email, subject, text_content, html_content, user_name)
            
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
        
        subject = "Reset Your Password"
        text_content = f"""
Hello {user_name},

You requested to reset your password. Click the link below to reset it:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email and your password will remain unchanged.
        """
        
        html_content = f"""
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
        
        # Try SendGrid first if available, fallback to SMTP
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_key:
            result = await send_email_via_sendgrid(email, subject, text_content, html_content, user_name)
            if result:
                return True
            print("[EMAIL] SendGrid failed, falling back to SMTP...")
        
        if not settings.smtp_user or not settings.smtp_password:
            print("[EMAIL ERROR] SMTP not configured and SendGrid not available")
            return False
        
        return await send_email_via_smtp(email, subject, text_content, html_content, user_name)
            
    except Exception as e:
        print(f"[EMAIL ERROR] Error sending password reset email: {e}")
        import traceback
        traceback.print_exc()
        return False
