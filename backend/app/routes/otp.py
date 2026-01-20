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
from app.models.otp import OTPRequest, OTPSendResponse, OTPVerify, OTPVerifyResponse, OTPInitByEmail
from app.models.user import EmailStr
from app.utils.security import (
    verify_session_token,
    create_access_token,
    create_session_token,
    generate_otp,
    hash_otp,
    verify_otp
)
from app.services.email_service import email_service
from app.config import settings

router = APIRouter()


def mask_email(email: str) -> str:
    """Mask email address for display (e.g., u***@example.com)."""
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_local = local[0] + "***" + local[-1] if len(local) > 2 else local[0] + "***"
        else:
            masked_local = local[0] + "***"
        return f"{masked_local}@{domain}"
    return "***@***"


@router.post("/init-otp-by-email", response_model=OTPSendResponse)
async def init_otp_by_email(request: OTPInitByEmail):
    """
    Initialize OTP verification by email.
    
    Flow:
    1. Look up user by email
    2. Get Aadhaar ID from user
    3. Look up email from Aadhaar-Email table
    4. Send OTP to that email
    5. Return session token for OTP verification
    
    This endpoint is designed to be called from external login components.
    """
    print(f"\n[INIT OTP BY EMAIL] Received request for email: {request.email}")
    users = get_users_collection()
    
    # Find user by email
    user = await users.find_one({"email": request.email})
    print(f"[INIT OTP BY EMAIL] User found: {user is not None}")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email"
        )
    
    user_id = str(user["_id"])
    aadhaar_id = user.get("aadhaar_id")
    user_name = user.get("name", "User")
    
    if not aadhaar_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an Aadhaar ID linked"
        )
    
    # Get email from aadhaar_phone collection (now stores email, not phone)
    aadhaar_phone = get_aadhaar_phone_collection()
    aadhaar_record = await aadhaar_phone.find_one({"aadhaar_id": aadhaar_id})
    
    if not aadhaar_record:
        # Fall back to user's email
        otp_email = user["email"]
    else:
        # Get email from aadhaar_phone collection (handles both old phone_no and new email fields)
        otp_email = aadhaar_record.get("email") or aadhaar_record.get("phone_no")
        if not otp_email:
            # If no email in aadhaar record, fall back to user's email
            otp_email = user["email"]
    
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
    
    # Send OTP via Email
    print(f"\n[OTP SEND] Email: {otp_email}, OTP: {otp}")
    result = await email_service.send_otp(otp_email, otp, user_name)
    print(f"[OTP SEND] Result: {result}\n")
    
    if not result["success"]:
        print(f"[OTP SEND ERROR] {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    # Create session token for OTP verification
    session_token = create_session_token(user_id, step="password_verified")
    
    response = OTPSendResponse(
        success=True,
        message=f"OTP sent to your registered email address",
        expires_in=settings.OTP_EXPIRY_SECONDS,
        phone_masked=mask_email(otp_email),  # Reusing phone_masked field for email_masked
        session_token=session_token  # Include session token in response
    )
    
    print(f"[INIT OTP BY EMAIL] Response: success={response.success}, session_token={'present' if response.session_token else 'missing'}")
    return response


@router.post("/send-otp", response_model=OTPSendResponse)
async def send_otp(request: OTPRequest):
    """
    Send OTP to user's email address linked to their Aadhaar.
    
    This is called after password verification succeeds.
    """
    # Verify session token from previous step
    payload = verify_session_token(request.session_token, required_step="password_verified")
    
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
    
    # Get Aadhaar ID from user
    aadhaar_id = user.get("aadhaar_id")
    user_name = user.get("name", "User")
    
    if not aadhaar_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an Aadhaar ID linked"
        )
    
    # Get email from aadhaar_phone collection (now stores email, not phone)
    aadhaar_phone = get_aadhaar_phone_collection()
    aadhaar_record = await aadhaar_phone.find_one({"aadhaar_id": aadhaar_id})
    
    if not aadhaar_record:
        # Fall back to user's email
        otp_email = user["email"]
    else:
        # Get email from aadhaar_phone collection (handles both old phone_no and new email fields)
        otp_email = aadhaar_record.get("email") or aadhaar_record.get("phone_no")
        if not otp_email:
            # If no email in aadhaar record, fall back to user's email
            otp_email = user["email"]
    
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
    
    # Send OTP via Email
    print(f"\n[OTP SEND] Email: {otp_email}, OTP: {otp}")
    result = await email_service.send_otp(otp_email, otp, user_name)
    print(f"[OTP SEND] Result: {result}\n")
    
    if not result["success"]:
        print(f"[OTP SEND ERROR] {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return OTPSendResponse(
        success=True,
        message=f"OTP sent to your registered email address",
        expires_in=settings.OTP_EXPIRY_SECONDS,
        phone_masked=mask_email(otp_email)  # Reusing phone_masked field for email_masked
    )


@router.post("/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp_endpoint(request: OTPVerify):
    """
    Step 2 of MFA: Verify OTP.
    
    Returns final access token on success.
    """
    # Verify session token from previous step
    payload = verify_session_token(request.session_token, required_step="password_verified")
    
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

