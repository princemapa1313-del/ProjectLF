"""
Lost & Finder — main.py
FastAPI entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from config import settings
from database import connect_db, close_db, get_db
from auth.utils import hash_password

from auth.routes import router as auth_router
from reports.routes import router as reports_router
from family.routes import router as family_router
from face.routes import router as face_router
from notifications.routes import router as notifications_router
from admin.routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    
    # Initialize default admin if not exists
    db = get_db()
    admin_exists = await db.admins.find_one({"email": settings.ADMIN_EMAIL})
    if not admin_exists:
        try:
            await db.admins.insert_one({
                "email": settings.ADMIN_EMAIL,
                "password_hash": hash_password(settings.ADMIN_PASSWORD[:72]),
                "name": "Super Admin",
                "created_at": datetime.utcnow().isoformat()
            })
            print(f"Created default admin: {settings.ADMIN_EMAIL}")
        except Exception as e:
            # If admin already exists (duplicate key), ignore
            print(f"Default admin already exists or insertion error: {e}")

    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Lost & Finder API",
    description="Backend API for Missing Person Portal",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(reports_router)
app.include_router(family_router)
app.include_router(face_router)
app.include_router(notifications_router)
app.include_router(admin_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Lost & Finder API", "status": "online"}
