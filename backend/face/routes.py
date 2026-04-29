"""
Lost & Finder — face/routes.py
API endpoints for searching persons by face
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from database import get_db
from auth.utils import get_current_user
from face.engine import generate_encoding, compare_faces

router = APIRouter(prefix="/face", tags=["Face Recognition"])

@router.post("/search")
async def search_by_face(
    photo: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    file_bytes = await photo.read()
    
    # 1. Generate encoding for uploaded image
    unknown_encoding = generate_encoding(file_bytes)
    if not unknown_encoding:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image")

    db = get_db()
    
    # 2. Fetch all reports with encodings
    # In a production app, we would use an ANN vector search (like Milvus or Mongo Atlas Vector Search)
    # For this portal, we'll do an in-memory scan (fine for <10,000 records)
    cursor = db.reports.find({"face_encoding": {"$exists": True, "$ne": []}})
    reports = await cursor.to_list(length=1000)

    from datetime import datetime
    from bson import ObjectId

    from face.engine import FACE_RECOGNITION_AVAILABLE
    
    matches = []
    for report in reports:
        known_encoding = report.get("face_encoding")
        if known_encoding:
            confidence = compare_faces(known_encoding, unknown_encoding)
            
            if confidence >= 60.0:
                matches.append({
                    "report_id": report["report_id"],
                    "photo_url": report["photo_url"],
                    "name": report.get("name", "Unknown"),
                    "location": report.get("location", ""),
                    "status": report.get("status", ""),
                    "confidence": round(confidence, 2)
                })
                
                # Send notification to the user who created this report
                reporter_id = report.get("reporter_id")
                if reporter_id and reporter_id != current_user["user_id"]:
                    notification = {
                        "user_id": ObjectId(reporter_id),
                        "message": f"A user uploaded a photo that matches {report.get('name', 'your reported missing person')} with {round(confidence, 2)}% confidence.",
                        "read": False,
                        "created_at": datetime.utcnow().isoformat(),
                        "report_id": report["report_id"]
                    }
                    await db.notifications.insert_one(notification)
    
    # Sort by highest confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Take top 5
    return {"matches": matches[:5]}
