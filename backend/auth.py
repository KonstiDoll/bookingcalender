"""
Authentication module for Ferienhaus Kalender
Simple JWT-based authentication with passwords from environment variables
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from fastapi import HTTPException, Header
from jose import JWTError, jwt

# Load environment variables
load_dotenv()


# Configuration
SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("SESSION_EXPIRY_MINUTES", "480"))  # 8 hours default


@dataclass
class User:
    """Authenticated user"""
    party_id: Optional[int]  # None for admin
    is_admin: bool
    username: str


# Party name to ID mapping (must match PARTIES in main.py)
PARTY_NAMES = {
    "Siggi & Mausi": 1,
    "Silke & Wolfi & Zoe": 2,
    "Claudi & Wolfram": 3,
    "Extern": 4,
}


def get_password_config() -> dict[str, str]:
    """Load passwords from environment variables"""
    return {
        "Siggi & Mausi": os.getenv("PARTY_1_PASSWORD", ""),
        "Silke & Wolfi & Zoe": os.getenv("PARTY_2_PASSWORD", ""),
        "Claudi & Wolfram": os.getenv("PARTY_3_PASSWORD", ""),
        "Extern": os.getenv("PARTY_4_PASSWORD", ""),
        "Admin": os.getenv("ADMIN_PASSWORD", ""),
    }


def verify_password(username: str, password: str) -> Optional[User]:
    """
    Verify username and password against environment variables.
    Returns User object if valid, None otherwise.
    """
    passwords = get_password_config()

    # Check if username exists
    if username not in passwords:
        return None

    # Check password (must be non-empty and match)
    expected_password = passwords[username]
    if not expected_password or password != expected_password:
        return None

    # Create user object
    if username == "Admin":
        return User(party_id=None, is_admin=True, username="Admin")
    else:
        party_id = PARTY_NAMES.get(username)
        return User(party_id=party_id, is_admin=False, username=username)


def create_session_token(user: User) -> str:
    """Create JWT token for authenticated user"""
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.username,
        "party_id": user.party_id,
        "is_admin": user.is_admin,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_session_token(token: str) -> Optional[User]:
    """Verify JWT token and return User object"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        if not username:
            return None

        return User(
            party_id=payload.get("party_id"),
            is_admin=payload.get("is_admin", False),
            username=username
        )
    except JWTError:
        return None


async def get_current_user(authorization: str = Header(None)) -> User:
    """
    FastAPI dependency to extract and validate user from Authorization header.
    Usage: current_user: User = Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Nicht authentifiziert"
        )

    # Extract token from "Bearer <token>"
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    user = verify_session_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Ungültige oder abgelaufene Sitzung"
        )

    return user


def can_modify_booking(user: User, party_id: int) -> bool:
    """Check if user is allowed to modify a booking for given party"""
    if user.is_admin:
        return True
    return user.party_id == party_id
