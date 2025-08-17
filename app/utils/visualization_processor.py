#!/usr/bin/env python3
"""
Visualization processor for generating charts and plots
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from typing import Dict, Any, List, Optional
import numpy as np

class VisualizationProcessor:
    """Handles data visualization and chart generation"""
    
    def __init__(self):
        self.chart_types = {
            'scatter': self._create_scatter_plot,
            'line': self._create_line_plot,
            'bar': self._create_bar_chart,
            'histogram': self._create_histogram,
            'box': self._create_box_plot,
            'pie': self._create_pie_chart,
            'heatmap': self._create_heatmap
        }
    
    def generate_chart(self, query: str, session_data: Dict, 
                      chart_type: str = None) -> Dict[str, Any]:
        """
        Generate a chart based on natural language query
        """
        try:
            # Determine chart type from query if not specified
            if not chart_type:
                chart_type = self._detect_chart_type(query)
            
            # Load dataframes from session
            dataframes = self._load_session_dataframes(session_data)
            
            # Extract data based on query
            chart_data = self._extract_chart_data(query, dataframes)
            
            if not chart_data:
                return {
                    'success': False,
                    'error': 'Could not extract data for visualization from the query.'
                }
            
            # Generate the chart
            if chart_type in self.chart_types:
                chart = self.chart_types[chart_type](chart_data, query)
            else:
                # Default to scatter plot
                chart = self._create_scatter_plot(chart_data, query)
            
            return {
                'success': True,
                'chart': chart,
                'chart_type': chart_type,
                'data_summary': self._generate_data_summary(chart_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating chart: {str(e)}'
            }
    
    def _detect_chart_type(self, query: str) -> str:
        """Detect chart type from natural language query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['scatter', 'plot', 'vs', 'versus', 'against']):
            return 'scatter'
        elif any(word in query_lower for word in ['line', 'trend', 'over time', 'timeline']):
            return 'line'
        elif any(word in query_lower for word in ['bar', 'count', 'frequency', 'distribution']):
            return 'bar'
        elif any(word in query_lower for word in ['histogram', 'distribution', 'range']):
            return 'histogram'
        elif any(word in query_lower for word in ['box', 'quartile', 'median']):
            return 'box'
        elif any(word in query_lower for word in ['pie', 'percentage', 'proportion']):
            return 'pie'
        elif any(word in query_lower for word in ['heatmap', 'correlation']):
            return 'heatmap'
        else:
            return 'scatter'  # default
    
    def _extract_chart_data(self, query: str, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Extract relevant data for chart generation"""
        # For now, use the first available dataframe
        if not dataframes:
            return None
        
        df_name = list(dataframes.keys())[0]
        df = dataframes[df_name]
        
        # Simple extraction based on common patterns
        query_lower = query.lower()
        
        # Look for column names in the query
        columns = df.columns.tolist()
        found_columns = []
        
        for col in columns:
            if col.lower() in query_lower:
                found_columns.append(col)
        
        # If no specific columns found, use first two numeric columns
        if len(found_columns) < 2:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                found_columns = numeric_cols[:2]
            elif len(columns) >= 2:
                found_columns = columns[:2]
        
        if len(found_columns) < 2:
            return None
        
        return {
            'dataframe': df,
            'x_column': found_columns[0],
            'y_column': found_columns[1],
            'columns': found_columns
        }
    
    def _create_scatter_plot(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a scatter plot"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        y_col = chart_data['y_column']
        
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Scatter Plot: {x_col} vs {y_col}",
            labels={x_col: x_col, y_col: y_col}
        )
        
        return {
            'type': 'scatter',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Scatter Plot: {x_col} vs {y_col}",
                'xaxis_title': x_col,
                'yaxis_title': y_col
            }
        }
    
    def _create_line_plot(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a line plot"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        y_col = chart_data['y_column']
        
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Line Plot: {y_col} over {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
        
        return {
            'type': 'line',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Line Plot: {y_col} over {x_col}",
                'xaxis_title': x_col,
                'yaxis_title': y_col
            }
        }
    
    def _create_bar_chart(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a bar chart"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        y_col = chart_data['y_column']
        
        # For bar charts, we might want to aggregate the data
        if df[y_col].dtype in ['int64', 'float64']:
            # If y is numeric, create a bar chart of values
            fig = px.bar(
                df, 
                x=x_col, 
                y=y_col,
                title=f"Bar Chart: {y_col} by {x_col}",
                labels={x_col: x_col, y_col: y_col}
            )
        else:
            # If y is categorical, count occurrences
            value_counts = df[x_col].value_counts()
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Bar Chart: Count of {x_col}",
                labels={'x': x_col, 'y': 'Count'}
            )
        
        return {
            'type': 'bar',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Bar Chart: {y_col} by {x_col}",
                'xaxis_title': x_col,
                'yaxis_title': y_col if df[y_col].dtype in ['int64', 'float64'] else 'Count'
            }
        }
    
    def _create_histogram(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a histogram"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        
        fig = px.histogram(
            df, 
            x=x_col,
            title=f"Histogram: Distribution of {x_col}",
            labels={x_col: x_col}
        )
        
        return {
            'type': 'histogram',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Histogram: Distribution of {x_col}",
                'xaxis_title': x_col,
                'yaxis_title': 'Frequency'
            }
        }
    
    def _create_box_plot(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a box plot"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        y_col = chart_data['y_column']
        
        fig = px.box(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Box Plot: {y_col} by {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
        
        return {
            'type': 'box',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Box Plot: {y_col} by {x_col}",
                'xaxis_title': x_col,
                'yaxis_title': y_col
            }
        }
    
    def _create_pie_chart(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a pie chart"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        
        value_counts = df[x_col].value_counts()
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Pie Chart: Distribution of {x_col}"
        )
        
        return {
            'type': 'pie',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': f"Pie Chart: Distribution of {x_col}"
            }
        }
    
    def _create_heatmap(self, chart_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create a correlation heatmap"""
        df = chart_data['dataframe']
        
        # Select only numeric columns for correlation
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {
                'success': False,
                'error': 'Need at least 2 numeric columns for correlation heatmap'
            }
        
        corr_matrix = numeric_df.corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Heatmap",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        return {
            'type': 'heatmap',
            'data': json.loads(fig.to_json()),
            'layout': {
                'title': 'Correlation Heatmap'
            }
        }
    
    def _generate_data_summary(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for the chart data"""
        df = chart_data['dataframe']
        x_col = chart_data['x_column']
        y_col = chart_data['y_column']
        
        summary = {
            'total_records': len(df),
            'x_column': {
                'name': x_col,
                'type': str(df[x_col].dtype),
                'unique_values': df[x_col].nunique()
            },
            'y_column': {
                'name': y_col,
                'type': str(df[y_col].dtype),
                'unique_values': df[y_col].nunique()
            }
        }
        
        # Add numeric statistics if applicable
        if df[x_col].dtype in ['int64', 'float64']:
            summary['x_column'].update({
                'mean': float(df[x_col].mean()),
                'std': float(df[x_col].std()),
                'min': float(df[x_col].min()),
                'max': float(df[x_col].max())
            })
        
        if df[y_col].dtype in ['int64', 'float64']:
            summary['y_column'].update({
                'mean': float(df[y_col].mean()),
                'std': float(df[y_col].std()),
                'min': float(df[y_col].min()),
                'max': float(df[y_col].max())
            })
        
        return summary
    
    def _load_session_dataframes(self, session_data: Dict) -> Dict[str, pd.DataFrame]:
        """Load dataframes from session data"""
        dataframes = {}
        
        if 'uploaded_files' in session_data:
            for file_info in session_data['uploaded_files']:
                try:
                    df = pd.read_csv(file_info['file_path'])
                    dataframes[file_info['filename']] = df
                except Exception as e:
                    print(f"Error loading {file_info['filename']}: {e}")
        
        return dataframes 