# MFA Secure Login System with Facial Recognition

A multi-factor authentication system featuring email/password login, facial recognition verification, and Aadhaar-linked phone OTP verification.

## Features

- **3-Factor Authentication**
  1. Email + Password verification
  2. Face recognition using webcam
  3. OTP verification via Aadhaar-linked phone number

- **Standalone Components**: Each authentication step is a self-contained HTML/CSS/JS component that can be embedded anywhere

- **Admin Tool**: Tkinter GUI for managing users and Aadhaar-phone mappings

- **Modern Stack**: FastAPI backend, MongoDB database, MSG91 OTP integration

## Project Structure

```
FAp2/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # MongoDB connection
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   └── services/          # Business logic
│   ├── requirements.txt
│   └── env.example.txt        # Environment template
├── admin/
│   └── admin_tool.py          # Tkinter admin GUI
├── components/                 # Standalone frontend components
│   ├── login/                 # Email/password login
│   ├── face-verify/           # Webcam face verification
│   ├── otp-verify/            # OTP input & verification
│   └── shared/
│       └── api.js             # Shared API utilities
└── demo/
    └── index.html             # Demo page with all components
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- MongoDB (running locally or connection string)
- Node.js (optional, for serving frontend)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note for face_recognition on Windows:**
You may need to install Visual Studio Build Tools and CMake first:
1. Install Visual Studio Build Tools with C++ workload
2. Install CMake: `pip install cmake`
3. Then: `pip install face_recognition`

On macOS, it's simpler:
```bash
brew install cmake
pip install face_recognition
```

### 2. Environment Configuration

Copy `env.example.txt` to `.env` and configure:

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=mfa_auth_db

# JWT (change in production!)
JWT_SECRET_KEY=your-super-secret-key

# MSG91 (get from msg91.com dashboard)
MSG91_AUTH_KEY=your-auth-key
MSG91_TEMPLATE_ID=your-template-id

# Face matching tolerance (0.6 is default, lower = stricter)
FACE_MATCH_TOLERANCE=0.6
```

### 3. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Add Test Users via Admin Tool

```bash
cd admin
python admin_tool.py
```

1. Go to "Add Aadhaar-Phone" tab
2. Add an Aadhaar ID and linked phone number
3. Go to "Add User" tab
4. Fill in user details and browse for a face photo
5. Click "Add User to Database"

### 5. Test the Demo

Open `demo/index.html` in a browser (use a local server for webcam access):

```bash
# Using Python
cd demo
python -m http.server 3000

# Or using Node
npx serve demo -p 3000
```

Visit: http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Step 1: Verify email/password |
| `/auth/verify-face` | POST | Step 2: Verify face encoding |
| `/auth/send-otp` | POST | Send OTP to Aadhaar-linked phone |
| `/auth/verify-otp` | POST | Step 3: Verify OTP, get access token |

## Component Usage

Each component can be used standalone:

```html
<!-- Include component files -->
<link rel="stylesheet" href="components/login/login.css">
<script src="components/shared/api.js"></script>
<script src="components/login/login.js"></script>

<!-- Initialize -->
<div id="my-container"></div>
<script>
MFALogin.init({
    container: '#my-container',
    apiUrl: 'http://localhost:8000',
    onSuccess: (result) => {
        console.log('Token:', result.sessionToken);
        // Proceed to next step
    },
    onError: (error) => {
        console.error(error);
    }
});
</script>
```

## Database Schema

### Users Collection
- email (unique)
- name
- password_hash
- face_encoding (128 floats)
- aadhaar_id (unique)
- phone_no

### AadhaarPhone Collection
- aadhaar_id (unique)
- phone_no

### OTPSessions Collection
- user_id
- otp_hash
- expires_at (TTL index)

## Development Notes

- **Cross-platform**: Developed on Windows, deployable on macOS
- **Face encoding**: 128-dimensional vector stored as array
- **OTP**: Hashed before storage, auto-expires via MongoDB TTL
- **Dev mode**: If MSG91 not configured, OTPs print to console

## Security Considerations

- Passwords hashed with bcrypt
- OTPs hashed before storage
- Session tokens are short-lived (10 min)
- Access tokens configurable expiry
- Face match tolerance configurable

## License

MIT

