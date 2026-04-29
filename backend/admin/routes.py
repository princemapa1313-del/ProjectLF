"""
Lost & Finder — admin/routes.py
Admin control panel API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth.utils import require_admin
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    db = get_db()
    cursor = db.users.find().sort("created_at", -1)
    users = await cursor.to_list(length=1000)
    return [{
        "id": str(u["_id"]),
        "name": u.get("name"),
        "email": u.get("email"),
        "mobile": u.get("mobile"),
        "is_active": u.get("is_active", True),
        "created_at": u.get("created_at")
    } for u in users]

@router.delete("/users/{id}")
async def delete_user(id: str, admin: dict = Depends(require_admin)):
    db = get_db()
    result = await db.users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User deleted"}

@router.get("/reports")
async def list_all_reports(admin: dict = Depends(require_admin)):
    db = get_db()
    cursor = db.reports.find().sort("created_at", -1)
    reports = await cursor.to_list(length=1000)
    return [{
        "id": str(r["_id"]),
        "report_id": r.get("report_id"),
        "name": r.get("name"),
        "status": r.get("status"),
        "created_at": r.get("created_at")
    } for r in reports]

@router.patch("/reports/{id}/status")
async def update_report_status(id: str, status: str, admin: dict = Depends(require_admin)):
    db = get_db()
    if status not in ["approved", "rejected", "found"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    result = await db.reports.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "success", "new_status": status}
