"""UI components for the Streamlit application."""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, List

from ..config.settings import settings
from ..data.models import GenerationParams  # Changed import


class UIComponents:
    """Reusable UI components."""
    
    @staticmethod
    def render_sidebar_generation_params() -> GenerationParams:
        """Render generation parameters in sidebar."""
        st.sidebar.header("🔧 Data Generation Parameters")
        
        with st.sidebar.expander("📊 Basic Parameters", expanded=True):
            n_participants = st.slider(
                "Number of Participants",
                min_value=settings.generation.participants['min'],
                max_value=settings.generation.participants['max'],
                value=settings.generation.participants['default'],
                step=settings.generation.participants['step']
            )
            
            avg_plans = st.slider(
                "Avg Plans per Participant",
                min_value=settings.generation.plans['avg_per_participant']['min'],
                max_value=settings.generation.plans['avg_per_participant']['max'],
                value=settings.generation.plans['avg_per_participant']['default'],
                step=settings.generation.plans['avg_per_participant']['step']
            )
            
            col1, col2 = st.columns(2)
            with col1:
                claims_min = st.number_input(
                    "Min Claims per Plan",
                    min_value=settings.generation.plans['claims_per_plan']['min'],
                    max_value=settings.generation.plans['claims_per_plan']['max'],
                    value=settings.generation.plans['claims_per_plan']['default_min']
                )
            
            with col2:
                claims_max = st.number_input(
                    "Max Claims per Plan",
                    min_value=settings.generation.plans['claims_per_plan']['min'],
                    max_value=settings.generation.plans['claims_per_plan']['max'],
                    value=settings.generation.plans['claims_per_plan']['default_max']
                )
        
        with st.sidebar.expander("📈 Utilization Parameters"):
            util_target = st.slider(
                "Target Mean Utilisation (%)",
                min_value=settings.generation.utilization['target']['min'],
                max_value=settings.generation.utilization['target']['max'],
                value=settings.generation.utilization['target']['default']
            )
            
            util_spread = st.slider(
                "Utilisation Spread (Beta b)",
                min_value=settings.generation.utilization['spread']['min'],
                max_value=settings.generation.utilization['spread']['max'],
                value=settings.generation.utilization['spread']['default']
            )
        
        with st.sidebar.expander("📅 Date Parameters"):
            pace_live = datetime.fromisoformat(
                st.text_input("PACE_LIVE Date", settings.dates.pace_live_default)
            )
            window_start = datetime.fromisoformat(
                st.text_input("Window Start", settings.dates.window_start_default)
            )
            window_end = datetime.fromisoformat(
                st.text_input("Window End", settings.dates.window_end_default)
            )
        
        with st.sidebar.expander("🎲 Random Seed"):
            seed = st.number_input(
                "Random Seed",
                min_value=0,
                max_value=99999999,
                value=settings.random_default_seed
            )
        
        return GenerationParams(
            n_participants=n_participants,
            avg_plans=avg_plans,
            claims_min=claims_min,
            claims_max=claims_max,
            util_target=util_target,
            util_spread=util_spread,
            seed=seed,
            pace_live=pace_live,
            window_start=window_start,
            window_end=window_end
        )
    
    @staticmethod
    def render_data_filters(df: pd.DataFrame, claims_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Render data filters and return filtered dataframes."""
        st.sidebar.header("🔍 Data Filters")
        
        with st.sidebar.expander("Geographic & Administrative", expanded=True):
            state_sel = st.multiselect(
                "State",
                options=sorted(df['State'].unique()),
                default=list(df['State'].unique())
            )
            
            mmm_sel = st.multiselect(
                "MMM Code",
                options=sorted(df['MMM_Code'].unique()),
                default=list(df['MMM_Code'].unique())
            )
        
        with st.sidebar.expander("Demographics"):
            age_sel = st.multiselect(
                "Age Band",
                options=sorted(df['Age_Band'].unique()),
                default=list(df['Age_Band'].unique())
            )
            
            dis_sel = st.multiselect(
                "Primary Disability",
                options=sorted(df['Primary_Disability'].unique()),
                default=list(df['Primary_Disability'].unique())
            )
        
        with st.sidebar.expander("Plan Management"):
            mgm_sel = st.multiselect(
                "Plan Management Mode",
                options=sorted(df['Plan_Management_Mode'].unique()),
                default=list(df['Plan_Management_Mode'].unique())
            )
            
            var_sel = st.multiselect(
                "Variation Type",
                options=sorted(df['Variation_Type'].unique()),
                default=list(df['Variation_Type'].unique())
            )
        
        with st.sidebar.expander("Support Items"):
            item_sel = st.multiselect(
                "Support Item Type",
                options=sorted(claims_df['Support_Item_Type'].unique()),
                default=None,
                help="Select specific support item types to analyze"
            )
            item_sel = item_sel or []
        
        # Apply filters
        df_filtered = df[
            df['State'].isin(state_sel) &
            df['MMM_Code'].isin(mmm_sel) &
            df['Age_Band'].isin(age_sel) &
            df['Primary_Disability'].isin(dis_sel) &
            df['Plan_Management_Mode'].isin(mgm_sel) &
            df['Variation_Type'].isin(var_sel)
        ]
        
        if item_sel:
            # Filter claims and then filter main data to matching plans
            claims_filtered = claims_df[claims_df['Support_Item_Type'].isin(item_sel)]
            matching_plans = claims_filtered['Plan_ID'].unique()
            df_filtered = df_filtered[df_filtered['Plan_ID'].isin(matching_plans)]
        else:
            claims_filtered = claims_df
        
        return df_filtered, claims_filtered
    
    @staticmethod
    def render_data_quality_metrics(quality_summary: Dict[str, Any]) -> None:
        """Render data quality metrics."""
        st.subheader("📈 Data Quality Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        main_data = quality_summary['main_data']
        claims_data = quality_summary['claims_data']
        
        with col1:
            st.metric(
                "Total Records",
                f"{main_data['total_records']:,}",
                help="Total number of plan records"
            )
        
        with col2:
            st.metric(
                "Participants",
                f"{main_data['total_participants']:,}",
                help="Unique participants in dataset"
            )
        
        with col3:
            st.metric(
                "Avg Utilization",
                f"{main_data['avg_utilization']}%",
                help="Average utilization rate across all plans"
            )
        
        with col4:
            st.metric(
                "Total Claims",
                f"{claims_data['total_claims']:,}",
                help="Total number of claims"
            )
    
    @staticmethod
    def render_export_options(df: pd.DataFrame, claims_df: pd.DataFrame) -> None:
        """Render data export options."""
        st.subheader("💾 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📊 Download Main Data (CSV)",
                data=df.to_csv(index=False),
                file_name=f"at_main_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                label="🧾 Download Claims Data (CSV)",
                data=claims_df.to_csv(index=False),
                file_name=f"at_claims_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col3:
            # Create summary report
            summary_data = {
                'Metric': [
                    'Total Participants',
                    'Total Plans',
                    'Total Claims',
                    'Average Utilization (%)',
                    'Total Budget (AUD)',
                    'Total Spent (AUD)'
                ],
                'Value': [
                    df['Hashed_Participant_ID'].nunique(),
                    len(df),
                    len(claims_df),
                    round(df['Utilization_Rate_Percent'].mean(), 2),
                    round(df['Capital_AT_Budget_Total_AUD'].sum(), 2),
                    round(df['Total_Spent_AUD'].sum(), 2)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            
            st.download_button(
                label="📋 Download Summary (CSV)",
                data=summary_df.to_csv(index=False),
                file_name=f"at_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
