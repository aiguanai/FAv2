"""
MSG91 OTP service integration.
"""
import httpx
from typing import Optional, Dict, Any

from app.config import settings


class MSG91Service:
    """MSG91 OTP service client."""
    
    BASE_URL = "https://control.msg91.com/api/v5"
    
    def __init__(self):
        self.auth_key = settings.MSG91_AUTH_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID
        self.sender_id = settings.MSG91_SENDER_ID
    
    async def send_otp(self, phone_number: str, otp: str) -> Dict[str, Any]:
        """
        Send OTP to phone number via MSG91.
        
        Args:
            phone_number: Phone number with country code (e.g., +919876543210)
            otp: The OTP to send
            
        Returns:
            Response dict with success status and message
        """
        # If no auth key configured, simulate sending
        if not self.auth_key:
            print(f"[DEV MODE] OTP for {phone_number}: {otp}")
            return {
                "success": True,
                "message": "OTP sent (dev mode - check console)",
                "request_id": "dev-mode"
            }
        
        # Prepare the request
        url = f"{self.BASE_URL}/flow/"
        
        # Remove + from phone number for MSG91
        mobile = phone_number.replace("+", "")
        
        headers = {
            "authkey": self.auth_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "template_id": self.template_id,
            "sender": self.sender_id,
            "short_url": "0",
            "mobiles": mobile,
            "VAR1": otp  # OTP variable in template
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "OTP sent successfully",
                        "request_id": data.get("request_id")
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to send OTP: {response.text}",
                        "request_id": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending OTP: {str(e)}",
                "request_id": None
            }
    
    async def verify_otp_via_api(self, phone_number: str, otp: str) -> bool:
        """
        Verify OTP via MSG91 API (optional - we handle verification locally).
        
        Note: We use local verification with hashed OTPs instead of MSG91's
        verify endpoint for better control and security.
        """
        # This is a placeholder if you want to use MSG91's verification
        # Currently we verify OTPs locally using hashed storage
        pass


# Singleton instance
msg91_service = MSG91Service()

