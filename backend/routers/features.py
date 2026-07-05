# Feature-importance and contribution endpoints.

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.feature_importance import FeatureImportanceService

router = APIRouter()


class ContributionRequest(BaseModel):
    feature_dict: Dict
    feature_vector: List[float]
    threat_score: int


@router.post("/contribution")
async def get_feature_contribution(request: ContributionRequest):
    try:
        result = FeatureImportanceService.get_top_contributors(
            feature_dict=request.feature_dict,
            feature_vector=request.feature_vector,
            threat_score=request.threat_score,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/global")
async def get_global_feature_importance():
    try:
        importances = FeatureImportanceService.get_global_importances()
        return {"importances": importances}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
