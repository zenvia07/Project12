"""
Email service for sending activation and password reset emails
Uses EmailJS HTTP API (works on Railway)
"""
import os
import httpx
from typing import Optional
from .database import settings


async def send_email_via_emailjs(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
    user_name: str,
    activation_url: str = None,
    reset_url: str = None
) -> bool:
    """Send email using EmailJS API"""
    try:
        # Validate EmailJS configuration
        if not settings.emailjs_service_id or not settings.emailjs_service_id.strip():
            print("[EMAIL ERROR] EMAILJS_SERVICE_ID not configured in Railway environment variables")
            return False
        
        if not settings.emailjs_template_id or not settings.emailjs_template_id.strip():
            print("[EMAIL ERROR] EMAILJS_TEMPLATE_ID not configured in Railway environment variables")
            return False
        
        if not settings.emailjs_public_key or not settings.emailjs_public_key.strip():
            print("[EMAIL ERROR] EMAILJS_PUBLIC_KEY not configured in Railway environment variables")
            return False
        
        # EmailJS API endpoint
        emailjs_url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # Prepare template parameters
        template_params = {
            "to_email": to_email,
            "to_name": user_name,
            "subject": subject,
            "message_html": html_content,
            "message_text": text_content,
        }
        
        # Add activation or reset URL if provided
        if activation_url:
            template_params["activation_url"] = activation_url
        if reset_url:
            template_params["reset_url"] = reset_url
        
        # Prepare request payload
        payload = {
            "service_id": settings.emailjs_service_id.strip(),
            "template_id": settings.emailjs_template_id.strip(),
            "user_id": settings.emailjs_public_key.strip(),
            "template_params": template_params
        }
        
        print(f"[EMAIL] Sending email via EmailJS to: {to_email}")
        print(f"[EMAIL] Using service_id: {settings.emailjs_service_id.strip()}")
        
        # Send request to EmailJS
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(emailjs_url, json=payload)
            
            if response.status_code == 200:
                print(f"[EMAIL SUCCESS] Email sent successfully via EmailJS to {to_email}")
                return True
            else:
                print(f"[EMAIL ERROR] EmailJS API error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"[EMAIL ERROR] EmailJS exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def send_activation_email(email: str, activation_token: str, user_name: str) -> bool:
    """Send account activation email"""
    try:
        print(f"[EMAIL] Attempting to send activation email to: {email}")
        
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
        
        # Send via EmailJS
        return await send_email_via_emailjs(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            user_name=user_name,
            activation_url=activation_url
        )
        
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
        
        # Send via EmailJS
        return await send_email_via_emailjs(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            user_name=user_name,
            reset_url=reset_url
        )
            
    except Exception as e:
        print(f"[EMAIL ERROR] Error sending password reset email: {e}")
        import traceback
        traceback.print_exc()
        return False
