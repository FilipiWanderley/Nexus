from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus Career AI"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str  # Service Role Key for Backend
    SUPABASE_JWT_SECRET: str # Required for python-jose validation
    
    # Gemini
    GEMINI_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
