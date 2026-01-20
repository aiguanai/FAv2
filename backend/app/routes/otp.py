"""
OTP verification routes.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database import (
    get_users_collection,
    get_aadhaar_phone_collection,
    get_otp_sessions_collection
)
from app.models.otp import OTPRequest, OTPSendResponse, OTPVerify, OTPVerifyResponse
from app.utils.security import (
    verify_session_token,
    create_access_token,
    generate_otp,
    hash_otp,
    verify_otp
)
from app.services.msg91_service import msg91_service
from app.config import settings

router = APIRouter()


@router.post("/send-otp", response_model=OTPSendResponse)
async def send_otp(request: OTPRequest):
    """
    Send OTP to user's phone number linked to their Aadhaar.
    
    This is called after face verification succeeds.
    """
    # Verify session token from previous step
    payload = verify_session_token(request.session_token, required_step="face_verified")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please login again."
        )
    
    user_id = payload["user_id"]
    
    # Get user from database
    users = get_users_collection()
    user = await users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get phone number from aadhaar_phone collection
    aadhaar_phone = get_aadhaar_phone_collection()
    aadhaar_record = await aadhaar_phone.find_one({"aadhaar_id": user["aadhaar_id"]})
    
    if not aadhaar_record:
        # Fall back to user's phone
        phone_number = user.get("phone_no")
        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No phone number linked to Aadhaar"
            )
    else:
        phone_number = aadhaar_record["phone_no"]
    
    # Generate OTP
    otp = generate_otp()
    otp_hash = hash_otp(otp)
    
    # Store OTP session
    otp_sessions = get_otp_sessions_collection()
    
    # Delete any existing OTP sessions for this user
    await otp_sessions.delete_many({"user_id": user_id})
    
    # Create new OTP session
    expires_at = datetime.utcnow() + timedelta(seconds=settings.OTP_EXPIRY_SECONDS)
    await otp_sessions.insert_one({
        "user_id": user_id,
        "otp_hash": otp_hash,
        "expires_at": expires_at,
        "verified": False,
        "created_at": datetime.utcnow()
    })
    
    # Send OTP via MSG91
    result = await msg91_service.send_otp(phone_number, otp)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return OTPSendResponse(
        success=True,
        message=f"OTP sent to your registered phone number",
        expires_in=settings.OTP_EXPIRY_SECONDS
    )


@router.post("/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp_endpoint(request: OTPVerify):
    """
    Step 3 of MFA: Verify OTP.
    
    Returns final access token on success.
    """
    # Verify session token from previous step
    payload = verify_session_token(request.session_token, required_step="face_verified")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please login again."
        )
    
    user_id = payload["user_id"]
    
    # Get OTP session
    otp_sessions = get_otp_sessions_collection()
    otp_session = await otp_sessions.find_one({
        "user_id": user_id,
        "verified": False
    })
    
    if not otp_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP request found. Please request a new OTP."
        )
    
    # Check if expired
    if datetime.utcnow() > otp_session["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    # Verify OTP
    if not verify_otp(request.otp, otp_session["otp_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP. Please try again."
        )
    
    # Mark OTP as verified
    await otp_sessions.update_one(
        {"_id": otp_session["_id"]},
        {"$set": {"verified": True}}
    )
    
    # Get user for access token
    users = get_users_collection()
    user = await users.find_one({"_id": ObjectId(user_id)})
    
    # Generate final access token
    access_token = create_access_token(user_id, user["email"])
    
    return OTPVerifyResponse(
        success=True,
        message="Authentication successful!",
        access_token=access_token,
        token_type="bearer"
    )

