"""
Authentication routes - email/password login.
"""
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database import get_users_collection
from app.models.user import UserLogin, LoginResponse, UserResponse
from app.utils.security import verify_password, create_session_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """
    Step 1 of MFA: Verify email and password.
    
    Returns a session token for the next step (face verification).
    """
    users = get_users_collection()
    
    # Find user by email
    user = await users.find_one({"email": credentials.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session token for next step
    user_id = str(user["_id"])
    session_token = create_session_token(user_id, step="password_verified")
    
    return LoginResponse(
        success=True,
        message="Password verified. Proceed to face verification.",
        session_token=session_token,
        user=UserResponse(
            email=user["email"],
            name=user["name"],
            aadhaar_id=user["aadhaar_id"]
        ),
        next_step="face_verification"
    )

