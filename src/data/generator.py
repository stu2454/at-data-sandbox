"""Data generation module for AT Data Sandbox."""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, List

from ..config.settings import settings
from .models import GenerationParams


class ATDataGenerator:
    """Generate synthetic AT data."""
    
    def __init__(self):
        self._support_items = self._generate_support_items()
    
    def _generate_support_items(self) -> List[str]:
        """Generate realistic support item codes."""
        return [f'05_{i:03d}_0101_1_{i*10}' for i in range(1, 41)]
    
    def _rand_hex(self, n: int = 8) -> str:
        """Generate random hex string."""
        return ''.join(random.choices('0123456789abcdef', k=n))
    
    def _rand_date(self, start: datetime, end: datetime) -> datetime:
        """Generate random date between start and end."""
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)
    
    def _age_band(self, age: int) -> str:
        """Convert age to age band."""
        band_start = (age // 5) * 5
        return f"{band_start}-{band_start + 4}"
    
    def generate_participants(self, n_participants: int) -> pd.DataFrame:
        """Generate participant data."""
        participants = []
        
        for _ in range(n_participants):
            age = random.randint(5, 70)
            participants.append({
                'Hashed_Participant_ID': self._rand_hex(),
                'State': random.choice(settings.lookup_data.states),
                'MMM_Code': random.choice(settings.lookup_data.mmm_codes),
                'Age_Band': self._age_band(age),
                'Primary_Disability': random.choice(settings.lookup_data.disabilities)
            })
        
        return pd.DataFrame(participants)
    
    def generate_plans(
        self, 
        participants_df: pd.DataFrame, 
        params: GenerationParams
    ) -> pd.DataFrame:
        """Generate plan data."""
        plans = []
        
        for pid in participants_df['Hashed_Participant_ID']:
            n_plans = max(1, int(np.random.poisson(params.avg_plans)))
            
            for _ in range(n_plans):
                start_date = self._rand_date(params.window_start, params.window_end)
                end_date = min(
                    start_date + timedelta(days=settings.generation.plans['duration_days']), 
                    params.window_end
                )
                
                plans.append({
                    'Plan_ID': self._rand_hex(),
                    'Hashed_Participant_ID': pid,
                    'Plan_Start_Date': start_date,
                    'Plan_End_Date': end_date,
                    'Capital_AT_Budget_Total_AUD': round(
                        random.uniform(
                            settings.generation.plans['budget']['min'],
                            settings.generation.plans['budget']['max']
                        ), 2
                    ),
                    'Plan_Management_Mode': random.choice(
                        settings.lookup_data.plan_management_modes
                    ),
                    'Variation_Type': random.choice(
                        settings.lookup_data.variation_types
                    )
                })
        
        return pd.DataFrame(plans)
    
    def generate_utilization_and_claims(
        self, 
        plans_df: pd.DataFrame, 
        params: GenerationParams
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate utilization and claims data."""
        utilization_records = []
        claim_records = []
        
        for _, plan in plans_df.iterrows():
            budget = plan['Capital_AT_Budget_Total_AUD']
            
            # Generate realistic utilization rate
            util_rate = min(
                np.random.beta(2, params.util_spread) * params.util_target / 100, 
                1.0
            )
            
            total_spent = round(budget * util_rate, 2)
            
            utilization_records.append({
                'Plan_ID': plan['Plan_ID'],
                'Utilization_Rate_Percent': round(util_rate * 100, 2),
                'Total_Spent_AUD': total_spent,
                'Avg_Processing_Days': random.randint(
                    settings.generation.processing_days['min'],
                    settings.generation.processing_days['max']
                )
            })
            
            # Generate claims
            n_claims = random.randint(params.claims_min, params.claims_max)
            
            if total_spent > 0:
                for _ in range(n_claims):
                    item = random.choice(self._support_items)
                    # Vary claim amounts around average
                    base_amount = total_spent / n_claims
                    amount = round(base_amount * random.uniform(0.8, 1.2), 2)
                    
                    claim_records.append({
                        'Plan_ID': plan['Plan_ID'],
                        'Support_Item_Type': item,
                        'Paid_UnitPrice_AUD': amount
                    })
        
        util_df = pd.DataFrame(utilization_records)
        claims_df = pd.DataFrame(claim_records)
        
        return util_df, claims_df
    
    def generate_complete_dataset(self, params: GenerationParams) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate complete synthetic dataset."""
        # Import validator here to avoid circular import
        from .validator import DataValidator
        
        validator = DataValidator()
        
        # Validate parameters
        validation_errors = validator.validate_generation_params(params)
        if validation_errors:
            raise ValueError(f"Invalid parameters: {validation_errors}")
        
        # Set random seeds
        random.seed(params.seed)
        np.random.seed(params.seed)
        
        try:
            # Generate data step by step
            participants_df = self.generate_participants(params.n_participants)
            plans_df = self.generate_plans(participants_df, params)
            util_df, claims_df = self.generate_utilization_and_claims(plans_df, params)
            
            # Merge main dataset
            main_df = (
                plans_df
                .merge(participants_df, on='Hashed_Participant_ID')
                .merge(util_df, on='Plan_ID')
            )
            
            # Final validation
            data_quality_issues = validator.validate_generated_data(main_df, claims_df)
            if data_quality_issues:
                # Log warnings but don't fail
                print(f"Data quality warnings: {data_quality_issues}")
            
            return main_df, claims_df
            
        except Exception as e:
            raise RuntimeError(f"Data generation failed: {e}")
