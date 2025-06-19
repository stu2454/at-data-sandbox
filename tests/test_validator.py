"""Tests for data validator."""

import pytest
import pandas as pd
from datetime import datetime

from src.data.validator import DataValidator
from src.data.models import GenerationParams  # Changed import


class TestDataValidator:
    """Test the data validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataValidator()
    
    def test_validate_valid_params(self):
        """Test validation of valid parameters."""
        params = GenerationParams(
            n_participants=100,
            avg_plans=1.2,
            claims_min=3,
            claims_max=8,
            util_target=60,
            util_spread=3,
            seed=12345,
            pace_live=datetime(2024, 7, 1),
            window_start=datetime(2023, 7, 1),
            window_end=datetime(2025, 6, 30)
        )
        
        errors = self.validator.validate_generation_params(params)
        assert len(errors) == 0
    
    def test_validate_invalid_participants(self):
        """Test validation of invalid participant count."""
        params = GenerationParams(
            n_participants=5000,  # Too high
            avg_plans=1.2,
            claims_min=3,
            claims_max=8,
            util_target=60,
            util_spread=3,
            seed=12345,
            pace_live=datetime(2024, 7, 1),
            window_start=datetime(2023, 7, 1),
            window_end=datetime(2025, 6, 30)
        )
        
        errors = self.validator.validate_generation_params(params)
        assert len(errors) > 0
        assert any("Participants must be between" in error for error in errors)
    
    def test_validate_invalid_claims(self):
        """Test validation of invalid claims parameters."""
        params = GenerationParams(
            n_participants=100,
            avg_plans=1.2,
            claims_min=10,  # Higher than max
            claims_max=5,
            util_target=60,
            util_spread=3,
            seed=12345,
            pace_live=datetime(2024, 7, 1),
            window_start=datetime(2023, 7, 1),
            window_end=datetime(2025, 6, 30)
        )
        
        errors = self.validator.validate_generation_params(params)
        assert len(errors) > 0
        assert any("Min claims cannot exceed max claims" in error for error in errors)
    
    def test_data_quality_summary(self):
        """Test data quality summary generation."""
        # Create sample data
        main_df = pd.DataFrame({
            'Plan_ID': ['A', 'B', 'C'],
            'Hashed_Participant_ID': ['P1', 'P2', 'P1'],
            'Utilization_Rate_Percent': [50.0, 75.0, 60.0]
        })
        
        claims_df = pd.DataFrame({
            'Plan_ID': ['A', 'A', 'B'],
            'Support_Item_Type': ['Item1', 'Item2', 'Item1'],
            'Paid_UnitPrice_AUD': [100.0, 200.0, 150.0]
        })
        
        summary = self.validator.get_data_quality_summary(main_df, claims_df)
        
        assert summary['main_data']['total_records'] == 3
        assert summary['main_data']['total_participants'] == 2
        assert summary['claims_data']['total_claims'] == 3
        assert summary['claims_data']['total_amount'] == 450.0
