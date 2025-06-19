"""Data validation module."""

from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from ..config.settings import settings
from .models import GenerationParams


class DataValidator:
    """Validate data generation parameters and output."""
    
    def validate_generation_params(self, params: GenerationParams) -> List[str]:
        """Validate generation parameters."""
        errors = []
        
        # Participant count validation
        min_p = settings.generation.participants['min']
        max_p = settings.generation.participants['max']
        if not (min_p <= params.n_participants <= max_p):
            errors.append(f"Participants must be between {min_p} and {max_p}")
        
        # Claims validation
        if params.claims_min > params.claims_max:
            errors.append("Min claims cannot exceed max claims")
        
        if params.claims_min < 1:
            errors.append("Min claims must be at least 1")
        
        # Utilization validation
        if not (0 <= params.util_target <= 100):
            errors.append("Utilization target must be between 0 and 100")
        
        if params.util_spread < 1:
            errors.append("Utilization spread must be at least 1")
        
        # Date validation
        if params.window_start >= params.window_end:
            errors.append("Window start must be before window end")
        
        if params.pace_live < params.window_start or params.pace_live > params.window_end:
            errors.append("PACE live date must be within the window")
        
        return errors
    
    def validate_generated_data(
        self, 
        main_df: pd.DataFrame, 
        claims_df: pd.DataFrame
    ) -> List[str]:
        """Validate generated data quality."""
        warnings = []
        
        # Check for required columns
        required_main_cols = [
            'Plan_ID', 'Hashed_Participant_ID', 'State', 'MMM_Code',
            'Primary_Disability', 'Utilization_Rate_Percent', 'Total_Spent_AUD'
        ]
        
        missing_cols = set(required_main_cols) - set(main_df.columns)
        if missing_cols:
            warnings.append(f"Missing main columns: {missing_cols}")
        
        # Check for nulls in critical columns
        for col in ['Plan_ID', 'Hashed_Participant_ID']:
            if col in main_df.columns and main_df[col].isnull().any():
                warnings.append(f"Null values found in {col}")
        
        # Check utilization rates
        if 'Utilization_Rate_Percent' in main_df.columns:
            invalid_util = main_df[
                (main_df['Utilization_Rate_Percent'] < 0) | 
                (main_df['Utilization_Rate_Percent'] > 100)
            ]
            if len(invalid_util) > 0:
                warnings.append(f"Invalid utilization rates: {len(invalid_util)} records")
        
        # Check claims data
        if claims_df.empty:
            warnings.append("No claims data generated")
        elif 'Paid_UnitPrice_AUD' in claims_df.columns:
            negative_amounts = claims_df[claims_df['Paid_UnitPrice_AUD'] < 0]
            if len(negative_amounts) > 0:
                warnings.append(f"Negative claim amounts: {len(negative_amounts)} records")
        
        return warnings
    
    def get_data_quality_summary(
        self, 
        main_df: pd.DataFrame, 
        claims_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get data quality summary statistics."""
        return {
            'main_data': {
                'total_records': len(main_df),
                'total_participants': main_df['Hashed_Participant_ID'].nunique() if 'Hashed_Participant_ID' in main_df.columns else 0,
                'total_plans': main_df['Plan_ID'].nunique() if 'Plan_ID' in main_df.columns else 0,
                'completeness_pct': round((main_df.notna().sum().sum() / main_df.size) * 100, 1),
                'avg_utilization': round(main_df['Utilization_Rate_Percent'].mean(), 2) if 'Utilization_Rate_Percent' in main_df.columns else 0
            },
            'claims_data': {
                'total_claims': len(claims_df),
                'total_amount': round(claims_df['Paid_UnitPrice_AUD'].sum(), 2) if 'Paid_UnitPrice_AUD' in claims_df.columns and not claims_df.empty else 0,
                'unique_items': claims_df['Support_Item_Type'].nunique() if 'Support_Item_Type' in claims_df.columns and not claims_df.empty else 0
            }
        }
