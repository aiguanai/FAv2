# Database Migration: Phone to Email

## What Changed

The `aadhaar_phone` collection now stores **email addresses** instead of phone numbers.

## Field Changes

**Old Schema:**
```json
{
  "aadhaar_id": "1234567890123456",
  "phone_no": "+919876543210"
}
```

**New Schema:**
```json
{
  "aadhaar_id": "1234567890123456",
  "email": "user@example.com"
}
```

## Migration Script (Optional)

If you have existing data with `phone_no`, you can migrate it:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["mfa_auth_db"]

# Find all entries with phone_no
entries = db.aadhaar_phone.find({"phone_no": {"$exists": True}})

for entry in entries:
    # Get user's email from users collection
    user = db.users.find_one({"aadhaar_id": entry["aadhaar_id"]})
    if user and user.get("email"):
        # Update to use email
        db.aadhaar_phone.update_one(
            {"_id": entry["_id"]},
            {"$set": {"email": user["email"]}, "$unset": {"phone_no": ""}}
        )
        print(f"Updated {entry['aadhaar_id']}: {user['email']}")
```

## Admin Tool Updates

- Tab renamed: "Add Aadhaar-Phone" → "Add Aadhaar-Email"
- Field changed: "Phone (+91)" → "Email"
- Validation: Now validates email format instead of phone format
- Display: Shows email addresses in the list

## Backward Compatibility

The code handles both old (`phone_no`) and new (`email`) formats for now, but new entries should use `email`.

