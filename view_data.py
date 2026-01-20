#!/usr/bin/env python3
"""
Simple script to view MongoDB data.
"""
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mfa_auth_db"]

def format_datetime(dt):
    """Format datetime for display."""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt

def print_collection(name, collection):
    """Print all documents in a collection."""
    print(f"\n{'='*60}")
    print(f"📊 {name.upper()}")
    print(f"{'='*60}")
    
    count = collection.count_documents({})
    print(f"Total documents: {count}\n")
    
    if count == 0:
        print("  (No documents found)\n")
        return
    
    for doc in collection.find():
        # Convert ObjectId to string for display
        doc_display = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc_display[key] = str(value)
            elif isinstance(value, datetime):
                doc_display[key] = format_datetime(value)
            elif key == "password_hash":
                # Mask password hash
                doc_display[key] = value[:20] + "..." if len(value) > 20 else value
            else:
                doc_display[key] = value
        
        print(json.dumps(doc_display, indent=2, default=str))
        print("-" * 60)

def main():
    """Main function."""
    print("\n🔍 MongoDB Data Viewer")
    print("=" * 60)
    
    # Test connection
    try:
        client.admin.command('ping')
        print("✓ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return
    
    # View Users collection
    print_collection("Users", db.users)
    
    # View AadhaarEmail collection (still named aadhaar_phone in DB)
    print_collection("Aadhaar-Email Links", db.aadhaar_phone)
    
    # View OTP Sessions collection
    print_collection("OTP Sessions", db.otp_sessions)
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

