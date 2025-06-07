from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "Stock Analysis"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    
    # Redis配置
    REDIS_URL: str
    
    # AKShare配置
    AKSHARE_TIMEOUT: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 