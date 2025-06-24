from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    booking_api_url: str
    booking_api_key: str
    database_url: str
    log_level: str = "INFO"
    jwt_secret: str
    allowed_origins: List[str] = []
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings() # type: ignore
