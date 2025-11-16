"""Configuration management for VeriMeet."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Meetstream API
    meetstream_api_key: str
    meetstream_api_url: str = "https://api.meetstream.ai"
    
    # OpenAI
    openai_api_key: str
    
    # Notion
    notion_api_key: str
    notion_database_id: str
    
    # Web Search (choose one)
    serper_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    
    # Server Configuration
    ngrok_url: str
    server_port: int = 8000
    server_host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

