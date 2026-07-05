# d:/SPECTER/phantomshield/backend/routers/education.py
# Education tip endpoints.

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from services.education_service import generate_education_tip, get_education_library

router = APIRouter()


class EducationRequest(BaseModel):
    attack_types: List[str]
    user_weak_spots: Optional[List[str]] = None


@router.post("/tip")
async def get_tip(request: EducationRequest):
    return generate_education_tip(
        attack_types=request.attack_types,
        user_weak_spots=request.user_weak_spots,
    )


@router.get("/tips")
async def get_tips_library():
    return {
        "count": len(get_education_library()),
        "tips": get_education_library(),
    }
