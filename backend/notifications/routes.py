"""
Lost & Finder — notifications/routes.py
API endpoints for real-time notifications (SSE/Polling) and history
"""
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth.utils import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def serialize_notif(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "message": doc.get("message", ""),
        "report_id": doc.get("report_id"),
        "match_id": doc.get("match_id"),
        "read": doc.get("read", False),
        "created_at": doc.get("created_at", "")
    }

@router.get("/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.notifications.find({"user_id": ObjectId(current_user["user_id"])}).sort("created_at", -1)
    notifs = await cursor.to_list(length=50)
    return [serialize_notif(n) for n in notifs]

@router.patch("/{id}/read")
async def mark_read(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.notifications.update_one(
        {"_id": ObjectId(id), "user_id": ObjectId(current_user["user_id"])},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}

@router.post("/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    db = get_db()
    await db.notifications.update_many(
        {"user_id": ObjectId(current_user["user_id"]), "read": False},
        {"$set": {"read": True}}
    )
    return {"status": "success"}
