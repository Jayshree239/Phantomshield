# d:/SPECTER/phantomshield/backend/models/db_models.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ScanResultRecord(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    scan_type: str
    input_value: str
    threat_score: int
    threat_level: str
    is_phishing: bool
    confidence: float
    attack_types: List[str] = []
    ai_explanation: Optional[str] = None
    scan_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None


class UserProfileRecord(BaseModel):
    user_id: str
    total_scans: int = 0
    phishing_caught: int = 0
    security_score: int = 50
    weak_spots: List[str] = []
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None


class EducationLogRecord(BaseModel):
    id: Optional[str] = None
    user_id: str
    tip_id: str
    category: str
    seen_at: Optional[datetime] = None
