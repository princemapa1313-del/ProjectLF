"""
Lost & Finder — auth/utils.py
JWT creation/verification and password hashing utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from config import settings

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    # Bcrypt only supports up to 72 bytes; truncate longer passwords
    plain_trunc = plain[:72]
    return pwd_context.hash(plain_trunc)

def verify_password(plain: str, hashed: str) -> bool:
    # Bcrypt only supports up to 72 bytes; truncate longer passwords
    plain_trunc = plain[:72]
    return pwd_context.verify(plain_trunc, hashed)

# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.JWT_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ── Dependency: current user ──────────────────────────────────────────────────

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    role: str = payload.get("role", "user")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return {"user_id": user_id, "role": role, "email": payload.get("email")}

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
