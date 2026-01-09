"""
Authentication API endpoints
Sign-up, login, logout, password reset

Author: Daniel J Rita (BATDAN)
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

from .database import UserDB, BetaDB, generate_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class BetaSignupRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    interest: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    subscription_tier: str
    beta_access: bool


# ============================================================================
# Helper Functions
# ============================================================================

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain letters"
    if not re.search(r'\d', password):
        return False, "Password must contain numbers"
    return True, ""


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency to get current user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Support both "Bearer token" and just "token"
    token = authorization.replace("Bearer ", "").strip()

    user = UserDB.get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, req: Request):
    """
    Create new account

    Returns token and user info on success
    """
    # Validate password
    valid, message = validate_password(request.password)
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    # Create user
    user_id = UserDB.create_user(
        email=request.email,
        password=request.password,
        name=request.name
    )

    if not user_id:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create session
    token = UserDB.create_session(
        user_id=user_id,
        ip=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )

    # Get user data
    user = UserDB.get_user_by_id(user_id)

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "subscription_tier": user["subscription_tier"],
            "beta_access": user["beta_access"]
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request):
    """
    Login with email and password

    Returns token and user info on success
    """
    user = UserDB.authenticate(request.email, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create session
    token = UserDB.create_session(
        user_id=user["id"],
        ip=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "subscription_tier": user["subscription_tier"],
            "beta_access": user["beta_access"]
        }
    }


@router.post("/logout")
async def logout(authorization: str = Header(None)):
    """
    Logout - invalidate session token
    """
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        UserDB.delete_session(token)

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get current user info
    """
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "subscription_tier": user["subscription_tier"],
        "beta_access": bool(user["beta_access"])
    }


@router.post("/verify-email/{token}")
async def verify_email(token: str):
    """
    Verify email address with token sent via email
    """
    success = UserDB.verify_email(token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    return {"message": "Email verified successfully"}


# ============================================================================
# Beta Signup Endpoints
# ============================================================================

@router.post("/beta-signup")
async def beta_signup(request: BetaSignupRequest):
    """
    Join the beta waitlist

    No account required - just email
    """
    success = BetaDB.add_signup(
        email=request.email,
        name=request.name,
        interest=request.interest
    )

    if not success:
        # Already signed up is still a success from user perspective
        return {"message": "You're on the list! We'll notify you when beta access is available."}

    return {"message": "Thanks for signing up! You'll be notified when beta access is available."}


@router.get("/beta-signups")
async def get_beta_signups(user: dict = Depends(get_current_user)):
    """
    Get all beta signups (admin only)
    """
    # Check if admin (simple check for now - owner email)
    if user["email"] != "danieljrita@hotmail.com":
        raise HTTPException(status_code=403, detail="Admin access required")

    signups = BetaDB.get_all_signups()
    return {
        "total": len(signups),
        "signups": signups
    }
