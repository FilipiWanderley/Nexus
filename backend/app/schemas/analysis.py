from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.scoring import ATSScoreResult

class KeywordImportance(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisRequest(BaseModel):
    resume_id: Optional[UUID] = None
    resume_text: Optional[str] = None
    job_description: str

class AnalysisCreate(BaseModel):
    resume_id: UUID
    job_description_id: UUID

class AnalysisResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_description_id: UUID
    match_score: Optional[int] = None
    summary: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class KeywordGapResponse(BaseModel):
    id: UUID
    keyword: str
    category: Optional[str] = None
    importance: KeywordImportance
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class RewriteSuggestionResponse(BaseModel):
    id: UUID
    section: str
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    reasoning: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RewriteRequest(BaseModel):
    original_text: str
    target_skills: List[str]
    seniority_level: str = "Mid-Level"

class RewriteResult(BaseModel):
    original_text: str
    rewritten_text: str
    explanation: str
    applied_keywords: List[str]

class OptimizeRequest(BaseModel):
    resume_id: Optional[UUID] = None
    resume_text: Optional[str] = None
    job_description: str
    missing_critical_skills: List[str] = []
    missing_bonus_skills: List[str] = []
    suggestions: List[str] = []

class OptimizeResult(BaseModel):
    optimized_resume_text: str
