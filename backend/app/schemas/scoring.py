from typing import List, Optional
from pydantic import BaseModel, Field

class KeywordMatch(BaseModel):
    keyword: str
    found: bool
    type: str  # "critical" or "bonus"

class ScoreBreakdown(BaseModel):
    keyword_score: float
    semantic_score: float
    seniority_score: float
    penalties: float

class ATSScoreResult(BaseModel):
    final_score: int
    breakdown: ScoreBreakdown
    missing_critical_skills: List[str]
    missing_bonus_skills: List[str]
    detected_yoe: Optional[float] = None
    required_yoe: Optional[float] = None
    explanation: str
    suggestions: List[str] = []

class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
