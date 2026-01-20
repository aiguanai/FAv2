# Email OTP Verification Component

A standalone Email OTP verification component with FastAPI backend and MongoDB database. Designed for integration into existing authentication systems.

## Features

- **Email OTP Verification** - Send and verify OTP codes via email
- **Standalone Component** - Self-contained HTML/CSS/JS component
- **Admin Tool** - Tkinter GUI for database initialization
- **FastAPI Backend** - RESTful API for OTP management
- **MongoDB Database** - User and OTP session storage

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
│   │       └── security.py # JWT, OTP generation
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
└── INTEGRATION_TROUBLESHOOTING.md  # Complete integration guide
```

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example.txt .env
# Edit .env with your MongoDB and SMTP settings
```

### 2. Initialize Database

Use the Admin Tool:
```bash
cd admin
python admin_tool.py
```

1. **Add User** tab: Create users with email, name, password, Aadhaar ID
2. **Add Aadhaar-Email** tab: Link Aadhaar IDs to email addresses (where OTP will be sent)

### 3. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Component

Open in browser:
```
http://localhost:3000/components/otp-verify/otp-verify.html?email=user@example.com
```

## Integration

See **[INTEGRATION_TROUBLESHOOTING.md](INTEGRATION_TROUBLESHOOTING.md)** for complete integration guide, API documentation, and troubleshooting.

### Quick Integration Example

```html
<!-- Option 1: Direct URL -->
<iframe src="http://your-domain/components/otp-verify/otp-verify.html?email=user@example.com"></iframe>

<!-- Option 2: Embedded Component -->
<div id="otp-container"></div>
<script src="components/shared/api.js"></script>
<script src="components/otp-verify/otp-verify.js"></script>
<script>
MFAOtpVerify.init({
    container: '#otp-container',
    apiUrl: 'http://localhost:8000',
    email: 'user@example.com',
    onSuccess: (result) => {
        console.log('Access token:', result.accessToken);
    }
});
</script>
```

## API Endpoints

- `POST /auth/init-otp-by-email` - Initialize OTP verification
- `POST /auth/send-otp` - Resend OTP (requires session token)
- `POST /auth/verify-otp` - Verify OTP code

See [INTEGRATION_TROUBLESHOOTING.md](INTEGRATION_TROUBLESHOOTING.md) for detailed API documentation.

## Configuration

### Environment Variables (`.env`)

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=mfa_auth_db

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRY_MINUTES=30

# Email SMTP (leave empty for dev mode)
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

**Dev Mode:** If `SMTP_USER` is empty, OTP codes will be printed to the backend console.

## Database Schema

### Users Collection
- `email` (unique)
- `name`
- `password_hash`
- `aadhaar_id` (unique, 16 digits)
- `phone_no` (optional)

### Aadhaar-Email Collection (`aadhaar_phone`)
- `aadhaar_id` (unique, 16 digits)
- `email` (email address where OTP is sent)

### OTP Sessions Collection
- `user_id`
- `otp_hash`
- `expires_at` (TTL index, auto-expires)

## Troubleshooting

For detailed troubleshooting, see **[INTEGRATION_TROUBLESHOOTING.md](INTEGRATION_TROUBLESHOOTING.md)**.

Common issues:
- **CORS Error** → Backend not running or not accessible
- **User not found** → Add user via Admin Tool
- **OTP not received** → Check SMTP settings or use dev mode
- **MongoDB connection error** → Ensure MongoDB is running

## Requirements

- Python 3.9+
- MongoDB (local or remote)
- SMTP server (Gmail, Outlook, or custom) - Optional for dev mode

## License

MIT
