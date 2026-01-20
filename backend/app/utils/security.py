"""
Security utilities for password hashing and JWT tokens.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(user_id: str, step: str = "password_verified") -> str:
    """
    Create a session token for MFA flow.
    
    Args:
        user_id: The user's ID
        step: Current authentication step
    """
    expire = datetime.utcnow() + timedelta(minutes=10)  # Short-lived for MFA
    payload = {
        "user_id": user_id,
        "step": step,
        "exp": expire,
        "type": "session"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_session_token(token: str, required_step: str) -> Optional[Dict[str, Any]]:
    """
    Verify a session token and check the step.
    
    Args:
        token: The session token
        required_step: The step this token should be at
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "session":
            return None
        if payload.get("step") != required_step:
            return None
        return payload
    except JWTError:
        return None


def create_access_token(user_id: str, email: str) -> str:
    """
    Create a final access token after all MFA steps complete.
    
    Args:
        user_id: The user's ID
        email: The user's email
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def generate_otp() -> str:
    """Generate a random OTP."""
    return "".join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])


def hash_otp(otp: str) -> str:
    """Hash an OTP for storage."""
    return pwd_context.hash(otp)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify an OTP against its hash."""
    return pwd_context.verify(plain_otp, hashed_otp)

