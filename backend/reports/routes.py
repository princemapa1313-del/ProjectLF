"""
Lost & Finder — reports/routes.py
CRUD routes for missing person reports
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from datetime import datetime
from bson import ObjectId
import uuid
import json

from database import get_db
from auth.utils import get_current_user, require_admin
from cloudinary_upload import upload_image
from face.engine import generate_encoding

router = APIRouter(prefix="/reports", tags=["Reports"])

def serialize_report(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "report_id": doc.get("report_id", ""),
        "photo_url": doc.get("photo_url", ""),
        "name": doc.get("name"),
        "age": doc.get("age"),
        "gender": doc.get("gender"),
        "clothes": doc.get("clothes"),
        "location": doc.get("location", ""),
        "date": doc.get("date", ""),
        "notes": doc.get("notes"),
        "contact": doc.get("contact", ""),
        "status": doc.get("status", "pending"),
        "reporter_id": str(doc.get("reporter_id")),
        "created_at": doc.get("created_at", "")
    }

@router.post("/")
async def create_report(
    photo: UploadFile = File(...),
    name: str = Form(""),
    age: str = Form(""),
    gender: str = Form(""),
    clothes: str = Form(""),
    location: str = Form(...),
    date: str = Form(...),
    notes: str = Form(""),
    contact: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    
    # Upload photo to Cloudinary
    file_bytes = await photo.read()
    try:
        upload_result = await upload_image(file_bytes, photo.content_type)
        photo_url = upload_result["url"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    # Generate unique report ID
    report_id = f"LF-{datetime.utcnow().strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"

    # Generate face encoding
    encoding = generate_encoding(file_bytes)
    
    doc = {
        "report_id": report_id,
        "photo_url": photo_url,
        "name": name,
        "age": int(age) if age.isdigit() else None,
        "gender": gender,
        "clothes": clothes,
        "location": location,
        "date": date,
        "notes": notes,
        "contact": contact,
        "status": "pending",  # Requires admin approval
        "reporter_id": ObjectId(current_user["user_id"]),
        "created_at": datetime.utcnow().isoformat(),
        "face_encoding": encoding
    }

    result = await db.reports.insert_one(doc)
    doc["_id"] = result.inserted_id

    return serialize_report(doc)

@router.get("/")
async def list_reports(status: str = "approved"):
    db = get_db()
    cursor = db.reports.find({"status": status}).sort("created_at", -1)
    reports = await cursor.to_list(length=100)
    return [serialize_report(r) for r in reports]

@router.get("/user/me")
async def list_my_reports(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.reports.find({"reporter_id": ObjectId(current_user["user_id"])}).sort("created_at", -1)
    reports = await cursor.to_list(length=100)
    return [serialize_report(r) for r in reports]

@router.get("/{id}")
async def get_report(id: str):
    db = get_db()
    # Search by report_id or internal _id
    query = {"_id": ObjectId(id)} if len(id) == 24 else {"report_id": id}
    doc = await db.reports.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return serialize_report(doc)

@router.get("/search/text")
async def search_reports_text(q: str):
    db = get_db()
    # Case-insensitive regex search across multiple fields
    query = {
        # Only allow searching approved reports or maybe all? We'll search approved for safety
        "status": "approved",
        "$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"clothes": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
            {"notes": {"$regex": q, "$options": "i"}}
        ]
    }
    cursor = db.reports.find(query).sort("created_at", -1)
    reports = await cursor.to_list(length=100)
    return [serialize_report(r) for r in reports]
