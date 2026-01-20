"""
Face verification routes.
"""
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.database import get_users_collection, get_aadhaar_phone_collection
from app.models.user import FaceVerifyRequest, FaceVerifyResponse
from app.utils.security import verify_session_token, create_session_token
from app.services.face_service import extract_encoding_from_base64, compare_faces

router = APIRouter()


def mask_phone_number(phone: str) -> str:
    """Mask phone number for display (e.g., +91****543210)."""
    if len(phone) >= 10:
        return phone[:3] + "****" + phone[-6:]
    return "****" + phone[-4:]


@router.post("/verify-face", response_model=FaceVerifyResponse)
async def verify_face(request: FaceVerifyRequest):
    """
    Step 2 of MFA: Verify face against stored encoding.
    
    Returns a session token for the next step (OTP verification).
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
    
    # Extract face encoding from submitted image
    submitted_encoding = extract_encoding_from_base64(request.face_image)
    
    if submitted_encoding is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face detected in the image. Please try again."
        )
    
    # Compare with stored encoding
    stored_encoding = user.get("face_encoding")
    
    if not stored_encoding:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User face encoding not found"
        )
    
    is_match, distance = compare_faces(stored_encoding, submitted_encoding)
    
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Face verification failed. Please try again."
        )
    
    # Get phone number for OTP (from aadhaar_phone collection)
    aadhaar_phone = get_aadhaar_phone_collection()
    aadhaar_record = await aadhaar_phone.find_one({"aadhaar_id": user["aadhaar_id"]})
    
    if not aadhaar_record:
        # Fall back to user's phone if no aadhaar mapping
        phone_number = user.get("phone_no", "")
    else:
        phone_number = aadhaar_record["phone_no"]
    
    # Create session token for next step
    session_token = create_session_token(user_id, step="face_verified")
    
    return FaceVerifyResponse(
        success=True,
        message="Face verified. OTP will be sent to your registered number.",
        session_token=session_token,
        next_step="otp_verification",
        phone_masked=mask_phone_number(phone_number)
    )

