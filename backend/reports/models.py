"""
Lost & Finder — reports/models.py
Pydantic models for Missing Person Reports
"""
from pydantic import BaseModel, Field
from typing import Optional

class ReportCreate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    clothes: Optional[str] = None
    location: str
    date: str
    notes: Optional[str] = None
    contact: str

class ReportResponse(BaseModel):
    id: str
    report_id: str
    photo_url: str
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    clothes: Optional[str]
    location: str
    date: str
    notes: Optional[str]
    contact: str
    status: str
    reporter_id: str
    created_at: str
