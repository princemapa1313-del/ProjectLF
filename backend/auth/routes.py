"""
Lost & Finder — auth/routes.py
Authentication routes: register, login, get current user
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from bson import ObjectId
from database import get_db
from auth.models import RegisterRequest, LoginRequest, TokenResponse
from auth.utils import hash_password, verify_password, create_access_token, get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "mobile": user["mobile"],
        "role": user.get("role", "user"),
        "created_at": user.get("created_at", ""),
        "is_active": user.get("is_active", True)
    }

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    db = get_db()

    # Check duplicate email
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "mobile": data.mobile,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({
        "sub": str(result.inserted_id),
        "email": data.email,
        "role": "user"
    })

    return TokenResponse(access_token=token, user=serialize_user(user_doc))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    db = get_db()

    # Check admin first
    admin = await db.admins.find_one({"email": data.email})
    if admin and verify_password(data.password, admin["password_hash"]):
        token = create_access_token({
            "sub": str(admin["_id"]),
            "email": admin["email"],
            "role": "admin"
        })
        return TokenResponse(access_token=token, user={
            "id": str(admin["_id"]),
            "name": admin.get("name", "Admin"),
            "email": admin["email"],
            "role": "admin"
        })

    # Check regular user
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account suspended")

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": "user"
    })
    return TokenResponse(access_token=token, user=serialize_user(user))


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    uid = current_user["user_id"]

    if current_user["role"] == "admin":
        admin = await db.admins.find_one({"_id": ObjectId(uid)})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return {
            "id": str(admin["_id"]),
            "name": admin.get("name", "Admin"),
            "email": admin["email"],
            "role": "admin"
        }

    user = await db.users.find_one({"_id": ObjectId(uid)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)
