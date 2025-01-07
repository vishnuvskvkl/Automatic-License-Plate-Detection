import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings configuration using pydantic."""
    
    yolo_model_path: str = os.path.join('app', 'models', 'best.pt')
    csv_file: str = os.path.join('app', 'data', 'license_plates.csv')
    camera_index: int = 0
    confidence_threshold: float = 0.8

    class Config:
        """Pydantic configuration class."""
        env_file = '.env'


settings = Settings()