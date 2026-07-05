# Gemini-powered deep analysis endpoints.

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.gemini_analyst import (
    analyze_url_anatomy,
    answer_scan_question,
    generate_threat_narrative,
)
from services.feature_importance import FeatureImportanceService

router = APIRouter()


class NarrativeRequest(BaseModel):
    url: str
    threat_score: int
    threat_level: str
    attack_types: List[str] = Field(default_factory=list)
    top_features: List[Dict] = Field(default_factory=list)
    is_phishing: bool = False


class QARequest(BaseModel):
    question: str
    url: str
    threat_score: int
    threat_level: str
    attack_types: List[str] = Field(default_factory=list)
    explanation_summary: str = ""
    conversation_history: Optional[List[Dict]] = None


class AnatomyRequest(BaseModel):
    url: str
    feature_dict: Dict = Field(default_factory=dict)
    attack_types: List[str] = Field(default_factory=list)


class ContributionRequest(BaseModel):
    feature_dict: Dict
    feature_vector: List[float]
    threat_score: int


@router.post("/narrative")
async def get_threat_narrative(request: NarrativeRequest):
    try:
        narrative = generate_threat_narrative(
            url=request.url,
            threat_score=request.threat_score,
            threat_level=request.threat_level,
            attack_types=request.attack_types,
            top_features=request.top_features,
            is_phishing=request.is_phishing,
        )
        return {"narrative": narrative}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ask")
async def ask_about_scan(request: QARequest):
    if len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question too short")
    if len(request.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long (max 500 chars)")

    try:
        answer = answer_scan_question(
            question=request.question,
            url=request.url,
            threat_score=request.threat_score,
            threat_level=request.threat_level,
            attack_types=request.attack_types,
            explanation_summary=request.explanation_summary,
            conversation_history=request.conversation_history,
        )
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/anatomy")
async def get_url_anatomy(request: AnatomyRequest):
    try:
        anatomy = analyze_url_anatomy(
            url=request.url,
            feature_dict=request.feature_dict,
            attack_types=request.attack_types,
        )
        return {"anatomy": anatomy}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/contribution")
async def get_feature_contribution(request: ContributionRequest):
    try:
        return FeatureImportanceService.get_top_contributors(
            feature_dict=request.feature_dict,
            feature_vector=request.feature_vector,
            threat_score=request.threat_score,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/features/global")
async def get_global_feature_importance():
    try:
        importances = FeatureImportanceService.get_global_importances()
        return {"importances": importances}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
