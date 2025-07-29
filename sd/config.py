
from pydantic import BaseSettings
from typing import Dict, List

class Settings(BaseSettings):
    # Similarity thresholds
    RULE_BASED_THRESHOLD: float = 0.7
    ML_THRESHOLD: float = 0.5
    
    # Field weights for rule-based approach
    FIELD_WEIGHTS: Dict[str, float] = {
        'email': 0.4,
        'name': 0.3,
        'phone': 0.2,
        'address': 0.1
    }
    
    # ML training parameters
    TRAINING_SAMPLES: int = 50000
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    
    # Address parsing settings
    ADDRESS_ABBREVIATIONS: Dict[str, str] = {
        'st': 'street', 'ave': 'avenue', 'rd': 'road',
        'dr': 'drive', 'blvd': 'boulevard', 'ln': 'lane',
        'ct': 'court', 'pl': 'place', 'cir': 'circle'
    }
    
    class Config:
        env_file = ".env"

settings = Settings()
