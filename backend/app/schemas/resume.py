from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any
from .common import TimestampSchema

class ResumeBase(BaseModel):
    file_name: str
    file_path: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    parsed_content: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None

class ResumeResponse(ResumeBase, TimestampSchema):
    id: UUID
    user_id: UUID
    parsed_content: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
