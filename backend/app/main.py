"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_mongodb, close_mongodb_connection
from app.routes import otp

app = FastAPI(
    title="MFA Authentication API",
    description="Multi-factor authentication with OTP verification",
    version="1.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    await connect_to_mongodb()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_mongodb_connection()


# Include routers
app.include_router(otp.router, prefix="/auth", tags=["OTP Verification"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "MFA Authentication API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests."""
    from fastapi import Response
    return Response(status_code=204)

