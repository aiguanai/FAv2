"""
User models for authentication.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    aadhaar_id: str = Field(..., pattern=r"^\d{12}$", description="12-digit Aadhaar ID")
    phone_no: str = Field(..., pattern=r"^\+91\d{10}$", description="Phone with +91 prefix")


class User(UserBase):
    """User model for creation (used by admin tool)."""
    password: str = Field(..., min_length=6)
    face_encoding: List[float] = Field(..., min_length=128, max_length=128)


class UserInDB(UserBase):
    """User model as stored in database."""
    id: Optional[str] = Field(None, alias="_id")
    password_hash: str
    face_encoding: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class UserLogin(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model (without sensitive data)."""
    email: EmailStr
    name: str
    aadhaar_id: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response after successful password verification."""
    success: bool
    message: str
    session_token: str
    user: UserResponse
    next_step: str = "face_verification"


class FaceVerifyRequest(BaseModel):
    """Face verification request."""
    session_token: str
    face_image: str = Field(..., description="Base64 encoded face image")


class FaceVerifyResponse(BaseModel):
    """Response after successful face verification."""
    success: bool
    message: str
    session_token: str
    next_step: str = "otp_verification"
    phone_masked: str = Field(..., description="Masked phone number for display")

