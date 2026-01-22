from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
