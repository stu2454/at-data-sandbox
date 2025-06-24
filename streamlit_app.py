"""Main Streamlit application for AT Data Sandbox."""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import our modules
from src.config.settings import settings, config_manager
from src.data.generator import ATDataGenerator
from src.data.validator import DataValidator
from src.data.models import GenerationParams  # Added import
from src.ui.components import UIComponents
from src.ui.charts import ChartGenerator

# Configure Streamlit
st.set_page_config(
    page_title=settings.app.page_title,
    page_icon="📊",
    layout=settings.app.layout,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def get_components():
    """Get application components (cached)."""
    return {
        'generator': ATDataGenerator(),
        'validator': DataValidator(),
        'ui': UIComponents(),
        'charts': ChartGenerator()
    }

components = get_components()

# Cache data generation
@st.cache_data
def generate_cached_data(params_dict):
    """Generate data with caching."""
    params = GenerationParams(**params_dict)
    return components['generator'].generate_complete_dataset(params)

def main():
    """Main application function."""
    
    # Title and description
    st.title(settings.app.title)
    st.markdown("""
    Generate and explore synthetic payments data with realistic 
    utilization patterns, demographics, and spending behaviors.
    """)
    
    # Development mode indicator
    if config_manager.is_development():
        st.info("🚧 Running in development mode")
    
    # Sidebar: Generation Parameters
    params = components['ui'].render_sidebar_generation_params()
    
    # Generate button
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        generate_clicked = st.button("🔄 Generate Data", type="primary")
    with col2:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    # Initialize session state
    if "df" not in st.session_state:
        st.session_state.df = None
        st.session_state.claims_df = None
        st.session_state.generation_time = None
    
    # Generate data on button click
    if generate_clicked:
        with st.spinner("Generating synthetic data..."):
            try:
                # Convert params to dict for caching
                params_dict = {
                    'n_participants': params.n_participants,
                    'avg_plans': params.avg_plans,
                    'claims_min': params.claims_min,
                    'claims_max': params.claims_max,
                    'util_target': params.util_target,
                    'util_spread': params.util_spread,
                    'seed': params.seed,
                    'pace_live': params.pace_live,
                    'window_start': params.window_start,
                    'window_end': params.window_end
                }
                
                df, claims_df = generate_cached_data(params_dict)
                
                st.session_state.df = df
                st.session_state.claims_df = claims_df
                st.session_state.generation_time = datetime.now()
                
                st.success(f"✅ Generated {len(df):,} plan records and {len(claims_df):,} claims!")
                
            except Exception as e:
                st.error(f"❌ Error generating data: {str(e)}")
                return
    
    # Display results if data exists
    if st.session_state.df is not None:
        df = st.session_state.df
        claims_df = st.session_state.claims_df
        
        # Data quality metrics
        quality_summary = components['validator'].get_data_quality_summary(df, claims_df)
        components['ui'].render_data_quality_metrics(quality_summary)
        
        # Data filters
        df_filtered, claims_filtered = components['ui'].render_data_filters(df, claims_df)
        
        # Show filter results
        if len(df_filtered) < len(df):
            st.info(f"📊 Showing {len(df_filtered):,} of {len(df):,} records after filtering")
        
        # Charts section
        st.header("📈 Data Visualizations")
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Utilization Analysis", 
            "🏢 Organizational Views", 
            "👥 Demographic Analysis", 
            "💰 Financial Analysis"
        ])
        
        with tab1:
            st.subheader("Utilisation Distribution")
            fig1 = components['charts'].utilization_histogram(df_filtered)
            st.plotly_chart(fig1, use_container_width=True)
            
            st.subheader("Processing Delay vs Utilisation")
            fig2 = components['charts'].processing_scatter(df_filtered)
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Utilisation by State")
                fig3 = components['charts'].utilization_by_category(
                    df_filtered, 'State', 'Average Utilisation by State'
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                st.subheader("Utilisation by MMM Code")
                fig4 = components['charts'].utilization_by_category(
                    df_filtered, 'MMM_Code', 'Average Utilisation by MMM Code'
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            st.subheader("Utilisation by Plan Management Mode")
            fig5 = components['charts'].utilization_boxplot(
                df_filtered, 'Plan_Management_Mode', 'Utilisation Distribution by Management Mode'
            )
            st.plotly_chart(fig5, use_container_width=True)
        
        with tab3:
            st.subheader("Utilisation by Primary Disability")
            fig6 = components['charts'].utilization_violin(
                df_filtered, 'Primary_Disability', 'Utilisation Distribution by Disability Type'
            )
            st.plotly_chart(fig6, use_container_width=True)
            
            st.subheader("Utilisation by Age Band")
            fig7 = components['charts'].utilization_by_category(
                df_filtered, 'Age_Band', 'Average Utilisation by Age Band'
            )
            st.plotly_chart(fig7, use_container_width=True)
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Spending by Support Item")
                fig8 = components['charts'].spending_by_support_item(claims_filtered)
                st.plotly_chart(fig8, use_container_width=True)
            
            with col2:
                st.subheader("Utilisation by Support Item")
                fig9 = components['charts'].utilization_by_support_item(df_filtered, claims_filtered)
                st.plotly_chart(fig9, use_container_width=True)
        
        # Data export section
        with st.expander("💾 Export Data", expanded=False):
            components['ui'].render_export_options(df_filtered, claims_filtered)
        
        # Sample data preview
        with st.expander("🔍 Data Preview", expanded=False):
            st.subheader("Sample of Generated Data")
            
            preview_tabs = st.tabs(["Main Data", "Claims Data"])
            
            with preview_tabs[0]:
                st.dataframe(
                    df_filtered.head(100), 
                    use_container_width=True,
                    height=300
                )
            
            with preview_tabs[1]:
                st.dataframe(
                    claims_filtered.head(100),
                    use_container_width=True,
                    height=300
                )
        
        # Generation info
        if st.session_state.generation_time:
            st.sidebar.success(
                f"✅ Data generated at {st.session_state.generation_time.strftime('%H:%M:%S')}"
            )
    
    else:
        # Welcome message
        st.info("""
        👈 **Get Started**: Adjust the generation parameters in the sidebar and click 
        **"Generate Data"** to create your synthetic AT dataset.
        
        **Features:**
        - 🎯 Realistic utilization patterns
        - 📊 Interactive filtering and visualization  
        - 💾 Data export capabilities
        - 🔄 Reproducible results with seed control
        """)
        
        # Show sample configuration
        with st.expander("ℹ️ About the Data Model"):
            st.markdown("""
            **Generated Data Includes:**
            
            **Participants:**
            - Demographics (age, state, disability type)
            - Market Making Mechanism (MMM) codes
            
            **Plans:**
            - AT budget allocations
            - Plan management modes
            - Variation types and date ranges
            
            **Utilization & Claims:**
            - Realistic spending patterns
            - Support item purchases
            - Processing delays
            """)

if __name__ == "__main__":
    main()
