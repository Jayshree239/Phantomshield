# d:/SPECTER/phantomshield/backend/models/scan_models.py
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ScanType(str, Enum):
    URL = "url"
    EMAIL = "email"
    SMS = "sms"


class ThreatLevel(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


class AttackType(str, Enum):
    HOMOGRAPH = "homograph"
    TYPOSQUATTING = "typosquatting"
    SUBDOMAIN_ATTACK = "subdomain_attack"
    BRAND_IMPERSONATION = "brand_impersonation"
    FAKE_SSL = "fake_ssl"
    URGENCY_MANIPULATION = "urgency_manipulation"
    CREDENTIAL_HARVESTING = "credential_harvesting"
    MALWARE_DISTRIBUTION = "malware_distribution"
    SPEAR_PHISHING = "spear_phishing"
    UNKNOWN = "unknown"


# REQUEST MODELS
class URLScanRequest(BaseModel):
    url: str
    user_id: Optional[str] = None
    context: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value or len(value) < 4:
            raise ValueError("URL too short")
        if len(value) > 2048:
            raise ValueError("URL too long")
        return value.strip()


class EmailScanRequest(BaseModel):
    subject: str
    sender: str
    body: str
    headers: Optional[Dict[str, str]] = None
    user_id: Optional[str] = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        if len(value) > 50000:
            raise ValueError("Email body too large (max 50KB)")
        return value


class SMSScanRequest(BaseModel):
    message: str
    sender_number: Optional[str] = None
    user_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if len(value) > 1600:
            raise ValueError("SMS too long")
        return value.strip()


# FEATURE MODELS
class URLFeatures(BaseModel):
    # Domain features
    domain_age_days: int
    domain_length: int
    subdomain_count: int
    has_ip_address: bool
    tld_suspicious: bool
    tld_value: str

    # SSL features
    has_ssl: bool
    ssl_valid: bool
    ssl_age_days: Optional[int]
    ssl_issuer_trusted: bool

    # URL structure
    url_length: int
    has_at_symbol: bool
    has_double_slash: bool
    redirect_count: int
    special_char_count: int
    digit_count: int
    hyphen_count: int

    # Homograph features
    has_homograph_chars: bool
    homograph_chars_found: List[str]
    has_unicode_chars: bool

    # Content features
    has_login_keyword: bool
    has_secure_keyword: bool
    has_verify_keyword: bool
    has_update_keyword: bool
    has_account_keyword: bool

    # External lookups
    in_phishtank: Optional[bool] = None
    in_virustotal: Optional[bool] = None
    alexa_rank: Optional[int] = None


# RESPONSE MODELS
class SuspiciousElement(BaseModel):
    element: str
    reason: str
    severity: str
    attack_type: AttackType
    position: Optional[str] = None


class ExplanationBlock(BaseModel):
    summary: str
    suspicious_elements: List[SuspiciousElement]
    attack_technique: str
    how_attacker_thinks: str
    safe_alternative: Optional[str]
    ai_explanation: str
    confidence_rationale: Optional[str] = None
    immediate_actions: List[str] = Field(default_factory=list)


class EducationTip(BaseModel):
    tip_id: str
    category: str
    title: str
    content: str
    example: str
    difficulty: str


class ScanResult(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    scan_id: str
    scan_type: ScanType
    input_value: str
    threat_score: int
    threat_level: ThreatLevel
    is_phishing: bool
    confidence: float
    attack_types: List[AttackType]
    feature_dict: Optional[Dict[str, Any]] = None
    feature_vector: Optional[List[float]] = None
    top_contributors: Optional[Dict[str, Any]] = None
    features: Optional[URLFeatures] = None
    explanation: Optional[ExplanationBlock] = None
    education_tip: Optional[EducationTip] = None
    scan_time_ms: int
    timestamp: datetime
    model_versions: Dict[str, str]


class BatchScanRequest(BaseModel):
    urls: List[str]
    user_id: Optional[str] = None

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, value: List[str]) -> List[str]:
        if len(value) > 50:
            raise ValueError("Maximum 50 URLs per batch")
        return value


class UserSecurityProfile(BaseModel):
    user_id: str
    total_scans: int
    phishing_caught: int
    security_score: int
    weak_spots: List[str]
    improvement_trend: str
    weekly_report: Dict[str, Any]
