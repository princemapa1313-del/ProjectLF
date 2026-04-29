"""
Lost & Finder — family/routes.py
CRUD routes for adding family members
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from datetime import datetime
from bson import ObjectId

from database import get_db
from auth.utils import get_current_user
from cloudinary_upload import upload_image
from face.engine import generate_encoding

router = APIRouter(prefix="/family", tags=["Family Members"])

def serialize_family(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "name": doc.get("name", ""),
        "relation": doc.get("relation", ""),
        "age": doc.get("age"),
        "marks": doc.get("marks", ""),
        "height": doc.get("height", ""),
        "last_seen_location": doc.get("last_seen_location", ""),
        "last_seen_date": doc.get("last_seen_date", ""),
        "photo_url": doc.get("photo_url", ""),
        "notes": doc.get("notes", ""),
        "created_at": doc.get("created_at", "")
    }

@router.post("/")
async def add_family_member(
    photo: UploadFile = File(...),
    name: str = Form(...),
    relation: str = Form(...),
    age: str = Form(""),
    marks: str = Form(""),
    height: str = Form(""),
    last_seen_location: str = Form(""),
    last_seen_date: str = Form(""),
    notes: str = Form(""),
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

    # Generate face encoding
    encoding = generate_encoding(file_bytes)

    doc = {
        "user_id": ObjectId(current_user["user_id"]),
        "name": name,
        "relation": relation,
        "age": int(age) if age.isdigit() else None,
        "marks": marks,
        "height": height,
        "last_seen_location": last_seen_location,
        "last_seen_date": last_seen_date,
        "photo_url": photo_url,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
        "face_encoding": encoding
    }

    result = await db.family_members.insert_one(doc)
    doc["_id"] = result.inserted_id

    return serialize_family(doc)

@router.get("/")
async def list_family_members(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.family_members.find({"user_id": ObjectId(current_user["user_id"])}).sort("created_at", -1)
    members = await cursor.to_list(length=100)
    return [serialize_family(m) for m in members]
