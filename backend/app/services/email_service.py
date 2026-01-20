"""
Email OTP service for sending OTP via email.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import asyncio

from app.config import settings


class EmailService:
    """Email service for sending OTP via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    async def send_otp(self, to_email: str, otp: str, user_name: str = None) -> Dict[str, Any]:
        """
        Send OTP to email address via SMTP.
        
        Args:
            to_email: Recipient email address
            otp: The OTP code to send
            user_name: Optional user name for personalization
            
        Returns:
            Response dict with success status and message
        """
        # If no SMTP configured, simulate sending
        if not self.smtp_host or not self.smtp_user:
            print(f"\n{'='*60}")
            print(f"[DEV MODE] OTP NOT SENT VIA EMAIL")
            print(f"To Email: {to_email}")
            print(f"OTP Code: {otp}")
            print(f"{'='*60}\n")
            return {
                "success": True,
                "message": "OTP sent (dev mode - check backend console for OTP)",
                "request_id": "dev-mode"
            }
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = "Your OTP Verification Code"
            
            # Email body
            name = user_name or "User"
            email_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #e94560;">OTP Verification Code</h2>
                  <p>Hello {name},</p>
                  <p>Your OTP verification code is:</p>
                  <div style="background: #f4f4f4; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                    <h1 style="color: #e94560; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp}</h1>
                  </div>
                  <p>This code will expire in 5 minutes.</p>
                  <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    If you didn't request this code, please ignore this email.
                  </p>
                </div>
              </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            OTP Verification Code
            
            Hello {name},
            
            Your OTP verification code is: {otp}
            
            This code will expire in 5 minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            # Attach both HTML and plain text
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(email_body, 'html'))
            
            # Send email using SMTP
            await asyncio.to_thread(self._send_smtp, msg, to_email)
            
            return {
                "success": True,
                "message": "OTP sent successfully to your email",
                "request_id": f"email-{to_email}"
            }
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            print(f"[EMAIL ERROR] {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "request_id": None
            }
    
    def _send_smtp(self, msg: MIMEMultipart, to_email: str):
        """Send email via SMTP (runs in thread to avoid blocking)."""
        try:
            # Connect to SMTP server
            if self.smtp_port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # TLS connection
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            # Login
            server.login(self.smtp_user, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"[EMAIL] OTP sent successfully to {to_email}")
            
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send: {str(e)}")
            raise


# Singleton instance
email_service = EmailService()

