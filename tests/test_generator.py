"""Tests for data generator."""

import pytest
import pandas as pd
from datetime import datetime

from src.data.generator import ATDataGenerator
from src.data.models import GenerationParams  # Changed import
from src.config.settings import settings


class TestATDataGenerator:
    """Test the AT data generator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ATDataGenerator()
        self.test_params = GenerationParams(
            n_participants=100,
            avg_plans=1.5,
            claims_min=3,
            claims_max=8,
            util_target=60,
            util_spread=3,
            seed=12345,
            pace_live=datetime(2024, 7, 1),
            window_start=datetime(2023, 7, 1),
            window_end=datetime(2025, 6, 30)
        )
    
    def test_generate_participants(self):
        """Test participant generation."""
        df = self.generator.generate_participants(50)
        
        assert len(df) == 50
        assert 'Hashed_Participant_ID' in df.columns
        assert 'State' in df.columns
        assert 'Primary_Disability' in df.columns
        
        # Check all states are valid
        assert df['State'].isin(settings.lookup_data.states).all()
        
        # Check no nulls in critical columns
        assert df['Hashed_Participant_ID'].notna().all()
    
    def test_generate_plans(self):
        """Test plan generation."""
        participants_df = self.generator.generate_participants(10)
        plans_df = self.generator.generate_plans(participants_df, self.test_params)
        
        assert len(plans_df) >= 10  # Should be at least one plan per participant
        assert 'Plan_ID' in plans_df.columns
        assert 'Capital_AT_Budget_Total_AUD' in plans_df.columns
        
        # Check budget ranges
        assert plans_df['Capital_AT_Budget_Total_AUD'].min() >= settings.generation.plans['budget']['min']
        assert plans_df['Capital_AT_Budget_Total_AUD'].max() <= settings.generation.plans['budget']['max']
    
    def test_generate_complete_dataset(self):
        """Test complete dataset generation."""
        df, claims_df = self.generator.generate_complete_dataset(self.test_params)
        
        # Basic structure tests
        assert len(df) >= self.test_params.n_participants
        assert len(claims_df) > 0
        
        # Check required columns exist
        required_cols = [
            'Plan_ID', 'Hashed_Participant_ID', 'State', 
            'Utilization_Rate_Percent', 'Total_Spent_AUD'
        ]
        for col in required_cols:
            assert col in df.columns
        
        # Check utilization rates are valid
        assert df['Utilization_Rate_Percent'].between(0, 100).all()
        
        # Check claims reference valid plans
        assert claims_df['Plan_ID'].isin(df['Plan_ID']).all()
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        df1, claims_df1 = self.generator.generate_complete_dataset(self.test_params)
        df2, claims_df2 = self.generator.generate_complete_dataset(self.test_params)
        
        # Should be identical
        pd.testing.assert_frame_equal(df1, df2)
        pd.testing.assert_frame_equal(claims_df1, claims_df2)
