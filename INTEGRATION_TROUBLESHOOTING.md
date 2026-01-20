# Email OTP Component - Integration & Troubleshooting Guide

## Project Overview

This project provides a **standalone Email OTP verification component** that can be integrated into any web application. It includes:

- **Email OTP Component** - Frontend component for OTP input and verification
- **Backend API** - FastAPI server for OTP generation and verification
- **Admin Tool** - Tkinter GUI for database initialization and user management

## Project Structure

```
FAp2/
├── backend/                 # FastAPI backend server
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── config.py       # Configuration (SMTP, MongoDB, etc.)
│   │   ├── database.py     # MongoDB connection
│   │   ├── models/         # Pydantic models
│   │   ├── routes/
│   │   │   └── otp.py      # OTP API endpoints
│   │   ├── services/
│   │   │   └── email_service.py  # Email sending service
│   │   └── utils/
│   │       └── security.py # JWT, OTP generation, password hashing
│   ├── requirements.txt
│   └── env.example.txt
│
├── admin/
│   └── admin_tool.py       # Tkinter GUI for database management
│
├── components/
│   ├── otp-verify/          # Email OTP component
│   │   ├── otp-verify.html
│   │   ├── otp-verify.css
│   │   └── otp-verify.js
│   └── shared/
│       └── api.js           # API utility functions
│
└── INTEGRATION_TROUBLESHOOTING.md  # This file
```

## Quick Start

### 1. Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example.txt .env
# Edit .env and configure:
# - MongoDB URL
# - SMTP settings (or leave empty for dev mode)
# - JWT secret key
```

### 2. Setup Database

**Option A: Using Admin Tool (Recommended)**
```bash
# From project root
cd admin
python admin_tool.py
```

**Option B: Manual MongoDB Setup**
- Install MongoDB
- Create database: `mfa_auth_db`
- Collections will be created automatically

### 3. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Connected to MongoDB: mfa_auth_db
```

### 4. Test the Component

Open in browser:
```
http://localhost:3000/components/otp-verify/otp-verify.html?email=user@example.com
```

(Replace with an email that exists in your database)

## Integration Steps

### Step 1: Add User to Database

Use the Admin Tool:
1. Open `admin/admin_tool.py`
2. Fill in user details:
   - Email
   - Name
   - Password
   - Aadhaar ID (16 digits)
   - Phone (optional, for user record)
3. Click "Add User to Database"

### Step 2: Add Aadhaar-Email Mapping

In Admin Tool:
1. Go to "Add Aadhaar-Email" tab
2. Enter:
   - Aadhaar ID (16 digits)
   - Email address (where OTP will be sent)
3. Click "Add Aadhaar-Email Link"

**Important:** The email in the Aadhaar-Email table is where the OTP will be sent, not the login email.

### Step 3: Integrate OTP Component

**Option A: Direct URL (Simplest)**
```html
<!-- After your friend's login succeeds, redirect to: -->
<iframe src="http://your-domain/components/otp-verify/otp-verify.html?email=user@example.com"></iframe>

<!-- Or redirect: -->
<script>
window.location.href = 'http://your-domain/components/otp-verify/otp-verify.html?email=' + userEmail;
</script>
```

**Option B: API Integration**
```javascript
// After login, call the API
const response = await fetch('http://localhost:8000/auth/init-otp-by-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: userEmail })
});

const data = await response.json();
// data.session_token - use for OTP verification
// data.phone_masked - masked email for display
```

**Option C: Embed Component**
```html
<div id="otp-container"></div>
<script src="components/shared/api.js"></script>
<script src="components/otp-verify/otp-verify.js"></script>
<script>
MFAOtpVerify.init({
    container: '#otp-container',
    apiUrl: 'http://localhost:8000',
    email: 'user@example.com',
    onSuccess: (result) => {
        console.log('OTP verified!', result);
        // result.accessToken - use this for authenticated requests
    },
    onError: (error) => {
        console.error('OTP error:', error);
    }
});
</script>
```

## API Endpoints

### POST `/auth/init-otp-by-email`

Initialize OTP verification by email.

**Request:**
```json
{
    "email": "user@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP sent to your registered email address",
    "expires_in": 300,
    "phone_masked": "u***@example.com",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Flow:**
1. Looks up user by email
2. Gets Aadhaar ID from user
3. Looks up email from `aadhaar_phone` collection
4. Sends OTP to that email
5. Returns session token

### POST `/auth/send-otp`

Resend OTP (requires session token).

**Request:**
```json
{
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP sent to your registered email address",
    "expires_in": 300,
    "phone_masked": "u***@example.com"
}
```

### POST `/auth/verify-otp`

Verify the OTP code.

**Request:**
```json
{
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "otp": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Authentication successful!",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## Configuration

### Backend Configuration (`.env` file)

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=mfa_auth_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30

# Email SMTP (Leave empty for dev mode)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=MFA Authentication

# OTP Settings
OTP_EXPIRY_SECONDS=300
OTP_LENGTH=6
```

### Dev Mode (No Email Configuration)

If you leave `SMTP_USER` empty, OTP will be printed to backend console:
```
============================================================
[DEV MODE] OTP NOT SENT VIA EMAIL
To Email: user@example.com
OTP Code: 123456
============================================================
```

## Troubleshooting

### Issue 1: CORS Error / NetworkError

**Symptoms:**
```
Cross-Origin Request Blocked
NetworkError when attempting to fetch resource
```

**Solutions:**
1. **Check if backend is running:**
   ```bash
   # Test backend
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Check port conflict:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # If port in use, use different port:
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   # Then update frontend apiUrl
   ```

4. **Verify CORS is enabled:**
   - Check `backend/app/main.py` - should have `allow_origins=["*"]`

### Issue 2: "User not found" Error

**Symptoms:**
```
404: User not found with this email
```

**Solutions:**
1. **Add user via Admin Tool:**
   - Open `admin/admin_tool.py`
   - Fill in user details
   - Click "Add User to Database"

2. **Verify user exists:**
   ```bash
   python view_data.py
   # Check users collection
   ```

### Issue 3: "No email linked to Aadhaar" Error

**Symptoms:**
```
OTP sent but to wrong email
```

**Solutions:**
1. **Add Aadhaar-Email mapping:**
   - Open Admin Tool
   - Go to "Add Aadhaar-Email" tab
   - Enter Aadhaar ID and Email
   - Click "Add Aadhaar-Email Link"

2. **Verify mapping exists:**
   ```bash
   python view_data.py
   # Check aadhaar_phone collection
   ```

### Issue 4: OTP Not Received in Email

**Symptoms:**
- OTP not appearing in inbox
- No error in backend

**Solutions:**

**If using Dev Mode:**
- Check backend console for OTP code
- Use that code to test

**If using SMTP:**
1. **Check spam/junk folder**
2. **Verify SMTP credentials:**
   - For Gmail: Use App Password (not regular password)
   - Get App Password: https://myaccount.google.com/apppasswords
3. **Check backend console for errors:**
   ```
   [EMAIL ERROR] ...
   ```
4. **Test SMTP connection:**
   ```python
   # Test email sending manually
   python -c "from app.services.email_service import email_service; import asyncio; asyncio.run(email_service.send_otp('test@example.com', '123456', 'Test'))"
   ```

### Issue 5: MongoDB Connection Error

**Symptoms:**
```
Connection refused
Could not connect to MongoDB
```

**Solutions:**
1. **Check if MongoDB is running:**
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

2. **Verify MongoDB URL in `.env`:**
   ```env
   MONGODB_URL=mongodb://localhost:27017
   ```

3. **Test connection:**
   ```bash
   mongosh mongodb://localhost:27017
   ```

### Issue 6: "Invalid OTP" Error

**Symptoms:**
- OTP code not working
- Always shows invalid

**Solutions:**
1. **Check OTP expiry:**
   - OTP expires in 5 minutes (300 seconds)
   - Request new OTP if expired

2. **Verify you're using correct OTP:**
   - Check email for latest OTP
   - Or check backend console if in dev mode

3. **Check session token:**
   - Make sure session token is valid
   - Don't use expired tokens

### Issue 7: Component Not Loading

**Symptoms:**
- Blank page
- JavaScript errors

**Solutions:**
1. **Check browser console (F12)**
2. **Verify file paths:**
   - `components/shared/api.js` exists
   - `components/otp-verify/otp-verify.js` exists
3. **Hard refresh (Ctrl+Shift+R)**
4. **Check if serving via HTTP (not file://):**
   ```bash
   # Serve via HTTP server
   python3 -m http.server 3000
   # Then open: http://localhost:3000/components/otp-verify/otp-verify.html
   ```

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "name": "User Name",
  "password_hash": "bcrypt_hash...",
  "aadhaar_id": "1234567890123456",
  "phone_no": "+919876543210",  // Optional
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

### Aadhaar-Email Collection (aadhaar_phone)
```json
{
  "_id": ObjectId("..."),
  "aadhaar_id": "1234567890123456",
  "email": "otp-email@example.com"  // Email where OTP is sent
}
```

### OTP Sessions Collection
```json
{
  "_id": ObjectId("..."),
  "user_id": "user_object_id",
  "otp_hash": "bcrypt_hash...",
  "expires_at": ISODate("..."),
  "verified": false,
  "created_at": ISODate("...")
}
```

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] MongoDB connection successful
- [ ] User added via Admin Tool
- [ ] Aadhaar-Email mapping added
- [ ] OTP component loads in browser
- [ ] API call succeeds (check Network tab)
- [ ] OTP received (email or console)
- [ ] OTP verification succeeds
- [ ] Access token received

## Common Integration Patterns

### Pattern 1: Redirect After Login
```javascript
// After successful login
const userEmail = loginResponse.email;
window.location.href = `/components/otp-verify/otp-verify.html?email=${userEmail}`;
```

### Pattern 2: Embedded Component
```javascript
// In your app
const otpContainer = document.getElementById('otp-container');

MFAOtpVerify.init({
    container: otpContainer,
    apiUrl: 'http://localhost:8000',
    email: userEmail,
    onSuccess: (result) => {
        // Store access token
        localStorage.setItem('accessToken', result.accessToken);
        // Redirect to main app
        window.location.href = '/dashboard';
    }
});
```

### Pattern 3: API-Only Integration
```javascript
// Your app handles UI, just calls API
async function sendOTP(email) {
    const response = await fetch('http://localhost:8000/auth/init-otp-by-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    return await response.json();
}

async function verifyOTP(sessionToken, otp) {
    const response = await fetch('http://localhost:8000/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken, otp })
    });
    return await response.json();
}
```

## Support

If you encounter issues:

1. **Check backend console** for error messages
2. **Check browser console** (F12) for JavaScript errors
3. **Check Network tab** (F12) for API request/response
4. **Verify database** using `view_data.py`
5. **Test API directly** using curl or Postman

## Quick Reference

**Backend URL:** `http://localhost:8000`  
**Frontend Component:** `components/otp-verify/otp-verify.html`  
**Admin Tool:** `admin/admin_tool.py`  
**Database:** MongoDB on `localhost:27017`  
**Database Name:** `mfa_auth_db`

