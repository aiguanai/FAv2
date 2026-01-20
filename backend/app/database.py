"""
MongoDB database connection and collections.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.config import settings


class Database:
    """MongoDB database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongodb():
    """Connect to MongoDB on application startup."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.DATABASE_NAME]
    
    # Create indexes
    await setup_indexes()
    
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_mongodb_connection():
    """Close MongoDB connection on application shutdown."""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


async def setup_indexes():
    """Create database indexes for performance and constraints."""
    # Users collection indexes
    await db.db.users.create_index("email", unique=True)
    await db.db.users.create_index("aadhaar_id", unique=True)
    
    # AadhaarPhone collection indexes
    await db.db.aadhaar_phone.create_index("aadhaar_id", unique=True)
    
    # OTP sessions - TTL index for auto-expiry
    await db.db.otp_sessions.create_index(
        "expires_at",
        expireAfterSeconds=0
    )
    
    print("Database indexes created")


# Collection accessors
def get_users_collection():
    """Get the users collection."""
    return db.db.users


def get_aadhaar_phone_collection():
    """Get the aadhaar_phone collection."""
    return db.db.aadhaar_phone


def get_otp_sessions_collection():
    """Get the otp_sessions collection."""
    return db.db.otp_sessions

