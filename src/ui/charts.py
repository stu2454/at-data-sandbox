"""Chart generation module."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Optional

from ..config.settings import settings


class ChartGenerator:
    """Generate interactive charts for the AT data."""
    
    def __init__(self):
        self.default_height = settings.charts.default_height
        self.color_palette = settings.charts.color_palette
    
    def utilization_histogram(self, df: pd.DataFrame) -> go.Figure:
        """Create utilization distribution histogram."""
        fig = px.histogram(
            df,
            x='Utilization_Rate_Percent',
            nbins=20,
            title='Utilisation Rate Distribution',
            labels={
                'Utilization_Rate_Percent': 'Utilisation Rate (%)',
                'count': 'Number of Plans'
            },
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            height=self.default_height,
            showlegend=False,
            title_x=0.5
        )
        
        # Add mean line
        mean_util = df['Utilization_Rate_Percent'].mean()
        fig.add_vline(
            x=mean_util,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_util:.1f}%"
        )
        
        return fig
    
    def processing_scatter(self, df: pd.DataFrame) -> go.Figure:
        """Create processing delay vs utilization scatter plot."""
        fig = px.scatter(
            df,
            x='Avg_Processing_Days',
            y='Utilization_Rate_Percent',
            trendline='ols',
            title='Processing Delay vs Utilisation Rate',
            labels={
                'Avg_Processing_Days': 'Average Processing Days',
                'Utilization_Rate_Percent': 'Utilisation Rate (%)'
            },
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5
        )
        
        return fig
    
    def utilization_by_category(
        self, 
        df: pd.DataFrame, 
        category: str, 
        title: str
    ) -> go.Figure:
        """Create utilization by category bar chart."""
        category_data = (
            df.groupby(category)['Utilization_Rate_Percent']
            .mean()
            .reset_index()
            .sort_values('Utilization_Rate_Percent', ascending=True)
        )
        
        fig = px.bar(
            category_data,
            x=category,
            y='Utilization_Rate_Percent',
            title=title,
            labels={
                'Utilization_Rate_Percent': 'Average Utilisation Rate (%)',
                category: category.replace('_', ' ')
            },
            color='Utilization_Rate_Percent',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def utilization_boxplot(
        self, 
        df: pd.DataFrame, 
        category: str, 
        title: str
    ) -> go.Figure:
        """Create utilization distribution box plot by category."""
        fig = px.box(
            df,
            x=category,
            y='Utilization_Rate_Percent',
            title=title,
            labels={
                'Utilization_Rate_Percent': 'Utilisation Rate (%)',
                category: category.replace('_', ' ')
            },
            color=category,
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5,
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        return fig
    
    def utilization_violin(
        self, 
        df: pd.DataFrame, 
        category: str, 
        title: str
    ) -> go.Figure:
        """Create utilization distribution violin plot by category."""
        fig = px.violin(
            df,
            x=category,
            y='Utilization_Rate_Percent',
            box=True,
            title=title,
            labels={
                'Utilization_Rate_Percent': 'Utilisation Rate (%)',
                category: category.replace('_', ' ')
            },
            color=category,
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5,
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        return fig
    
    def spending_by_support_item(self, claims_df: pd.DataFrame) -> go.Figure:
        """Create spending by support item bar chart."""
        if claims_df.empty:
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(
                text="No claims data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(
                height=self.default_height,
                title="Total Spending by Support Item Type"
            )
            return fig
        
        spending_data = (
            claims_df.groupby('Support_Item_Type')['Paid_UnitPrice_AUD']
            .sum()
            .reset_index()
            .sort_values('Paid_UnitPrice_AUD', ascending=True)
        )
        
        fig = px.bar(
            spending_data,
            x='Support_Item_Type',
            y='Paid_UnitPrice_AUD',
            title='Total Spending by Support Item Type',
            labels={
                'Paid_UnitPrice_AUD': 'Total Spending (AUD)',
                'Support_Item_Type': 'Support Item Type'
            },
            color='Paid_UnitPrice_AUD',
            color_continuous_scale='blues'
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def utilization_by_support_item(
        self, 
        df: pd.DataFrame, 
        claims_df: pd.DataFrame
    ) -> go.Figure:
        """Create average utilization by support item chart."""
        if claims_df.empty:
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(
                text="No claims data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(
                height=self.default_height,
                title="Average Utilisation by Support Item Type"
            )
            return fig
        
        # Merge to get utilization rates for each support item
        util_by_item = (
            df[['Plan_ID', 'Utilization_Rate_Percent']]
            .merge(claims_df[['Plan_ID', 'Support_Item_Type']], on='Plan_ID')
            .groupby('Support_Item_Type')['Utilization_Rate_Percent']
            .mean()
            .reset_index()
            .sort_values('Utilization_Rate_Percent', ascending=True)
        )
        
        fig = px.bar(
            util_by_item,
            x='Support_Item_Type',
            y='Utilization_Rate_Percent',
            title='Average Utilisation by Support Item Type',
            labels={
                'Utilization_Rate_Percent': 'Average Utilisation Rate (%)',
                'Support_Item_Type': 'Support Item Type'
            },
            color='Utilization_Rate_Percent',
            color_continuous_scale='plasma'
        )
        
        fig.update_layout(
            height=self.default_height,
            title_x=0.5,
            xaxis_tickangle=-45
        )
        
        return fig
