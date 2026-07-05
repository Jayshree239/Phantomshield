# d:/SPECTER/phantomshield/backend/routers/explain.py
# Explanation endpoints.

from fastapi import APIRouter
from pydantic import BaseModel

from services.explainer_service import generate_explanation

router = APIRouter()


class ExplainRequest(BaseModel):
    url: str
    feature_dict: dict
    threat_score: int
    threat_level: str


@router.post("/url")
async def explain_url(request: ExplainRequest):
    explanation = await generate_explanation(
        url=request.url,
        feature_dict=request.feature_dict,
        threat_score=request.threat_score,
        threat_level=request.threat_level,
    )
    return {
        "url": request.url,
        "threat_score": request.threat_score,
        "threat_level": request.threat_level,
        "explanation": explanation,
    }
