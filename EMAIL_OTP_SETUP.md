# Email OTP Setup Guide

## Quick Setup

### Option 1: Dev Mode (No Configuration Needed)

1. **Leave SMTP settings empty in `.env`:**
   ```env
   SMTP_USER=
   SMTP_PASSWORD=
   ```

2. **OTP will be printed to backend console:**
   ```
   ============================================================
   [DEV MODE] OTP NOT SENT VIA EMAIL
   To Email: user@example.com
   OTP Code: 123456
   ============================================================
   ```

3. **Use that OTP code to test verification**

### Option 2: Gmail SMTP (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter name: "MFA App"
   - Copy the 16-character app password

3. **Update your `.env` file:**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   FROM_EMAIL=your-email@gmail.com
   FROM_NAME=MFA Authentication
   ```

4. **Restart your backend server**

### Option 3: Other Email Providers

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

**Custom SMTP:**
```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-password
```

## Testing

1. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test OTP:**
   - Open: `http://localhost:3000/components/otp-verify/otp-verify.html?email=your-email@example.com`
   - OTP will be sent to that email
   - Check your email inbox (and spam folder)

## Benefits of Email OTP

✅ **No DLT Required** - Works for all countries  
✅ **Easy Setup** - Just SMTP credentials  
✅ **Free/Cheap** - Most providers offer free tier  
✅ **Reliable** - High delivery rates  
✅ **No Regulatory Issues** - No TRAI/DLT compliance needed  

## Troubleshooting

**Email not received:**
- Check spam/junk folder
- Verify SMTP credentials are correct
- Check backend console for errors
- For Gmail: Make sure you're using App Password, not regular password

**SMTP Connection Error:**
- Verify SMTP_HOST and SMTP_PORT are correct
- Check if your network allows SMTP connections
- Some providers require specific ports (587 for TLS, 465 for SSL)

**Authentication Failed:**
- For Gmail: Use App Password, not regular password
- Enable "Less secure app access" (if available) or use App Password
- Verify SMTP_USER and SMTP_PASSWORD are correct

