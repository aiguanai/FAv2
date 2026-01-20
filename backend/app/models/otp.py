"""
OTP session models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OTPSession(BaseModel):
    """OTP session as stored in database."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    otp_hash: str
    expires_at: datetime
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class OTPRequest(BaseModel):
    """Request to send OTP."""
    session_token: str


class OTPInitByEmail(BaseModel):
    """Initialize OTP by email - looks up Aadhaar and phone automatically."""
    email: str = Field(..., description="User's email address")


class OTPSendResponse(BaseModel):
    """Response after OTP is sent."""
    success: bool
    message: str
    expires_in: int = Field(..., description="Seconds until OTP expires")
    phone_masked: str = Field(..., description="Masked email/phone for display (email_masked for email OTP)")
    session_token: Optional[str] = Field(None, description="Session token for OTP verification (only for init-otp-by-email)")


class OTPVerify(BaseModel):
    """OTP verification request."""
    session_token: str
    otp: str = Field(..., pattern=r"^\d{6}$", description="6-digit OTP")


class OTPVerifyResponse(BaseModel):
    """Response after successful OTP verification."""
    success: bool
    message: str
    access_token: str
    token_type: str = "bearer"


class AadhaarEmail(BaseModel):
    """Aadhaar-Email mapping model."""
    id: Optional[str] = Field(None, alias="_id")
    aadhaar_id: str = Field(..., pattern=r"^\d{16}$")
    email: str = Field(..., description="Email address linked to Aadhaar")
    
    class Config:
        populate_by_name = True

