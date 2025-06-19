"""Data models and structures for AT Data Sandbox."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class GenerationParams:
    """Parameters for data generation."""
    n_participants: int
    avg_plans: float
    claims_min: int
    claims_max: int
    util_target: int
    util_spread: int
    seed: int
    pace_live: datetime
    window_start: datetime
    window_end: datetime


@dataclass
class DataQualitySummary:
    """Data quality summary statistics."""
    main_data: Dict[str, Any]
    claims_data: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
