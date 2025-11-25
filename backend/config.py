from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Application
    APP_NAME: str = "AIRBAND HR"
    APP_VERSION: str = "1.1.7"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://192.168.20.53:3000,https://hgd09pzcrcm.sn.mynetname.net"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
