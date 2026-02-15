# CHECKPOINT_2_AUTHENTICATION
"""
Authentication API
==================
Username-only authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timedelta
import jwt
from uuid import UUID

from backend.config import settings
from backend.database.client import get_database
from backend.utils.logger import get_logger

logger = get_logger("auth_api")
router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================
# Request/Response Models
# ============================================

class LoginRequest(BaseModel):
    """Login request with username only"""
    username: str = Field(..., min_length=3, max_length=50)
    
    @validator("username")
    def username_must_be_valid(cls, v):
        """Validate username format"""
        if not v.isalnum() and '_' not in v:
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()


class LoginResponse(BaseModel):
    """Login response with user data and token"""
    user_id: str
    username: str
    display_name: Optional[str]
    access_token: str
    token_type: str = "bearer"
    created_at: datetime


class UserResponse(BaseModel):
    """User data response"""
    user_id: str
    username: str
    display_name: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool


# ============================================
# Helper Functions
# ============================================

def create_access_token(user_id: str, username: str) -> str:
    """
    Create JWT access token for user session.
    
    Args:
        user_id: User UUID
        username: Username
    
    Returns:
        JWT token string
    """
    # Token expires in 7 days
    expire = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    # Use a secret key from config (in production, use proper secret)
    secret = settings.SUPABASE_KEY[:32]  # Use first 32 chars as secret
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    return token


def verify_access_token(token: str) -> dict:
    """
    Verify JWT access token and extract payload.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload dict
        
    Raises:
        HTTPException if token is invalid
    """
    try:
        secret = settings.SUPABASE_KEY[:32]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================
# Authentication Endpoints
# ============================================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login or create user with username only (no password).
    
    - If username exists: Return existing user with new token
    - If username is new: Create user and return with token
    
    This is intentionally simple for educational purposes.
    In production, use proper OAuth/password authentication.
    """
    logger.info(f"Login attempt for username: {request.username}")
    
    try:
        db = await get_database()
        
        # Check if user exists
        user = await db.get_user_by_username(request.username)
        
        if user:
            # Existing user - update last login
            logger.info(f"Existing user found: {user['id']}")
            await db.update_user_last_login(user["id"])
        else:
            # New user - create account
            logger.info(f"Creating new user: {request.username}")
            user = await db.create_user(
                username=request.username,
                display_name=request.username.capitalize()
            )
            logger.info(f"New user created: {user['id']}")
        
        # Generate access token
        token = create_access_token(
            user_id=str(user["id"]),
            username=user["username"]
        )
        
        return LoginResponse(
            user_id=str(user["id"]),
            username=user["username"],
            display_name=user.get("display_name"),
            access_token=token,
            created_at=user["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """
    Get current user information from token.
    
    Query Parameters:
        token: JWT access token
    """
    # Verify token
    payload = verify_access_token(token)
    user_id = payload["sub"]
    
    try:
        db = await get_database()
        user = await db.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=str(user["id"]),
            username=user["username"],
            display_name=user.get("display_name"),
            created_at=user["created_at"],
            last_login=user.get("last_login"),
            is_active=user.get("is_active", True)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@router.post("/logout")
async def logout(token: str):
    """
    Logout user (client-side token removal).
    
    In a simple system, logout is handled client-side by removing the token.
    This endpoint exists for logging purposes.
    """
    payload = verify_access_token(token)
    username = payload["username"]
    
    logger.info(f"User logged out: {username}")
    
    return {"message": "Logged out successfully"}


@router.get("/validate")
async def validate_token(token: str):
    """
    Validate if a token is still valid.
    
    Query Parameters:
        token: JWT access token
    """
    try:
        payload = verify_access_token(token)
        return {
            "valid": True,
            "user_id": payload["sub"],
            "username": payload["username"],
            "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat()
        }
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail
        }
