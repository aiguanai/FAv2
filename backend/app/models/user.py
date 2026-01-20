"""
User models for authentication.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    aadhaar_id: str = Field(..., pattern=r"^\d{16}$", description="16-digit Aadhaar ID")
    phone_no: str = Field(..., pattern=r"^\+91\d{10}$", description="Phone with +91 prefix")


class User(UserBase):
    """User model for creation (used by admin tool)."""
    password: str = Field(..., min_length=6)


class UserInDB(UserBase):
    """User model as stored in database."""
    id: Optional[str] = Field(None, alias="_id")
    password_hash: str
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
    next_step: str = "otp_verification"

