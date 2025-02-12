from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    token: str
    db_url: str
    db_name: str
    host: str
    port: str
    user: str
    passw: str
    
    class Config:
        env_file = ".env"
        
settings = Settings()