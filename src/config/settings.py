"""Configuration management for AT Data Sandbox."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AppConfig:
    """Application configuration."""
    title: str
    page_title: str
    layout: str


@dataclass
class GenerationConfig:
    """Data generation configuration."""
    participants: Dict[str, Any]
    plans: Dict[str, Any]
    utilization: Dict[str, Any]
    processing_days: Dict[str, Any]


@dataclass
class LookupData:
    """Business lookup data."""
    states: list
    mmm_codes: list
    disabilities: list
    plan_management_modes: list
    variation_types: list


@dataclass
class ChartConfig:
    """Chart configuration."""
    default_height: int
    color_palette: list


@dataclass
class DateConfig:
    """Date configuration."""
    pace_live_default: str
    window_start_default: str
    window_end_default: str


@dataclass
class Settings:
    """Main settings container."""
    app: AppConfig
    generation: GenerationConfig
    lookup_data: LookupData
    charts: ChartConfig
    dates: DateConfig
    random_default_seed: int


class ConfigManager:
    """Configuration manager."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Settings] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = Path(__file__).parent / "config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
            
            self._config = Settings(
                app=AppConfig(**raw_config['app']),
                generation=GenerationConfig(**raw_config['generation']),
                lookup_data=LookupData(**raw_config['lookup_data']),
                charts=ChartConfig(**raw_config['charts']),
                dates=DateConfig(**raw_config['dates']),
                random_default_seed=raw_config['random']['default_seed']
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    @property
    def config(self) -> Settings:
        """Get configuration."""
        if self._config is None:
            self._load_config()
        return self._config
    
    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with fallback."""
        return os.getenv(key, default)
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.get_env_var('STREAMLIT_ENV', 'production') == 'development'


# Global instance
config_manager = ConfigManager()
settings = config_manager.config
