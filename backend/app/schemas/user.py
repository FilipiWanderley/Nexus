from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class User(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    
    class Config:
        from_attributes = True
