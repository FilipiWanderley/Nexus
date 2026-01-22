from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from enum import Enum
from .common import TimestampSchema

class JobStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"

class JobDescriptionBase(BaseModel):
    title: str
    company: str
    url: Optional[str] = None
    raw_text: Optional[str] = None
    status: JobStatus = JobStatus.SAVED

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    raw_text: Optional[str] = None
    status: Optional[JobStatus] = None

class JobDescriptionResponse(JobDescriptionBase, TimestampSchema):
    id: UUID
    user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
