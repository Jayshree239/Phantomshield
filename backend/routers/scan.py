# d:/SPECTER/phantomshield/backend/routers/scan.py
# Main scan API endpoints.

import asyncio
import time
import uuid
from datetime import datetime

from fastapi import APIRouter
from requests import request

from config import settings
from models.scan_models import (
    AttackType,
    BatchScanRequest,
    EmailScanRequest,
    SMSScanRequest,
    ScanResult,
    ScanType,
    URLScanRequest,
)
from services.education_service import generate_education_tip
from services.email_scanner import extract_urls_from_email, score_email_text
from services.explainer_service import generate_explanation_bundle
from services.feature_importance import FeatureImportanceService
from services.sms_scanner import extract_urls_from_sms, score_sms_text
from services.supabase_service import get_user_weak_spots, save_scan_result
from services.url_scanner import scan_url_features

router = APIRouter()


@router.post("/url", response_model=ScanResult)
async def scan_url(request: URLScanRequest):
    start_time = time.time()

    import asyncio

    scan_payload = await asyncio.to_thread(
        scan_url_features,
        request.url
    )
    feature_vector = scan_payload["feature_vector"]
    feature_dict = scan_payload["feature_dict"]
    prediction = scan_payload["prediction"]
    attack_types = scan_payload["attack_types"]
    response_feature_dict = {key: value for key, value in feature_dict.items() if not key.startswith("_")}

    top_contributors = FeatureImportanceService.get_top_contributors(
        feature_dict=feature_dict,
        feature_vector=feature_vector,
        threat_score=prediction["threat_score"],
    )

    explanation_payload = None
    education_tip = None

    if prediction["threat_score"] >= 40:
        user_weak_spots = []
        if request.user_id:
            user_weak_spots = await get_user_weak_spots(request.user_id)

        explanation_payload = await generate_explanation_bundle(
            url=request.url,
            feature_dict=feature_dict,
            threat_score=prediction["threat_score"],
            threat_level=prediction["threat_level"],
        )

        education_tip = generate_education_tip(
            attack_types=[attack.value for attack in attack_types],
            user_weak_spots=user_weak_spots,
        )

    result = {
        "scan_id": str(uuid.uuid4()),
        "scan_type": ScanType.URL,
        "input_value": request.url,
        "threat_score": prediction["threat_score"],
        "threat_level": prediction["threat_level"],
        "is_phishing": prediction["is_phishing"],
        "confidence": prediction["confidence"],
        "attack_types": attack_types,
        "feature_dict": response_feature_dict,
        "feature_vector": feature_vector,
        "top_contributors": top_contributors,
        "features": None,
        "explanation": explanation_payload if prediction["threat_score"] >= 40 else None,
        "education_tip": education_tip,
        "scan_time_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.utcnow(),
        "model_versions": {
            "random_forest": "1.0.0",
            "xgboost": "1.0.0",
            "explainer": settings.GEMINI_MODEL,
        },
    }

    if request.user_id:
        try:
            await save_scan_result(
                user_id=request.user_id,
                scan_data=result,
                attack_types=[attack.value for attack in attack_types],
            )
        except Exception:
            pass

    return result


@router.post("/batch", response_model=list[ScanResult])
async def scan_batch(request: BatchScanRequest):
    results = []
    for url in request.urls:
        result = await scan_url(URLScanRequest(url=url, user_id=request.user_id))
        results.append(result)
    return results


@router.post("/email", response_model=ScanResult)
async def scan_email(request: EmailScanRequest):
    urls_in_body = extract_urls_from_email(request.body)

    if urls_in_body:
        result = await scan_url(URLScanRequest(url=urls_in_body[0], user_id=request.user_id))
        result["scan_type"] = ScanType.EMAIL
        result["input_value"] = f"FROM: {request.sender} | SUBJECT: {request.subject}"
        return result

    start_time = time.time()
    threat_score = score_email_text(request.body)

    return {
        "scan_id": str(uuid.uuid4()),
        "scan_type": ScanType.EMAIL,
        "input_value": f"FROM: {request.sender}",
        "threat_score": threat_score,
        "threat_level": "suspicious" if threat_score > 40 else "safe",
        "is_phishing": threat_score > 50,
        "confidence": 0.70,
        "attack_types": [AttackType.URGENCY_MANIPULATION] if threat_score > 0 else [AttackType.UNKNOWN],
        "features": None,
        "explanation": None,
        "education_tip": generate_education_tip(
            attack_types=["urgency_manipulation"] if threat_score > 0 else ["default"],
            user_weak_spots=None,
        ),
        "scan_time_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.utcnow(),
        "model_versions": {"text_analyzer": "1.0.0"},
    }


@router.post("/sms", response_model=ScanResult)
async def scan_sms(request: SMSScanRequest):
    urls_in_sms = extract_urls_from_sms(request.message)

    if urls_in_sms:
        result = await scan_url(URLScanRequest(url=urls_in_sms[0], user_id=request.user_id))
        result["scan_type"] = ScanType.SMS
        result["input_value"] = request.message[:100]
        return result

    start_time = time.time()
    threat_score = score_sms_text(request.message)

    return {
        "scan_id": str(uuid.uuid4()),
        "scan_type": ScanType.SMS,
        "input_value": request.message[:100],
        "threat_score": threat_score,
        "threat_level": "suspicious" if threat_score > 40 else "safe",
        "is_phishing": threat_score > 50,
        "confidence": 0.65,
        "attack_types": [AttackType.URGENCY_MANIPULATION] if threat_score > 0 else [AttackType.UNKNOWN],
        "features": None,
        "explanation": None,
        "education_tip": generate_education_tip(
            attack_types=["urgency_manipulation"] if threat_score > 0 else ["default"],
            user_weak_spots=None,
        ),
        "scan_time_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.utcnow(),
        "model_versions": {"sms_analyzer": "1.0.0"},
    }
