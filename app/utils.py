"""
Utility Functions Module
=========================
Shared utility functions used across the application.
"""

import streamlit as st
from typing import List, Dict, Any
import pandas as pd


# ========================================
# FORMATTING UTILITIES
# ========================================

def format_temperature(value: float, unit: str = "C") -> str:
    """Format temperature value with unit."""
    return f"{value:.1f}°{unit}"


def format_discharge(value: float, unit: str = "m³/s") -> str:
    """Format discharge value with unit."""
    return f"{value:.2f} {unit}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage."""
    return f"{value:.{decimals}f}%"


# ========================================
# VALIDATION UTILITIES
# ========================================

def validate_year_range(start_year: int, end_year: int) -> tuple:
    """
    Validate and return year range.
    
    Returns:
        Tuple of (valid, error_message)
    """
    if start_year > end_year:
        return False, "Start year must be before end year"
    
    if start_year < 1961 or end_year > 2100:
        return False, "Years must be between 1961 and 2100"
    
    return True, ""


def validate_months(months: List[str]) -> tuple:
    """
    Validate month list.
    
    Returns:
        Tuple of (valid, month_numbers, error_message)
    """
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    if not months:
        return False, [], "At least one month must be selected"
    
    month_nums = []
    for month in months:
        month_lower = month.lower()[:3]
        if month_lower in month_map:
            month_nums.append(month_map[month_lower])
        else:
            return False, [], f"Invalid month: {month}"
    
    return True, sorted(month_nums), ""


# ========================================
# CACHING UTILITIES
# ========================================

def clear_cache():
    """Clear Streamlit cache."""
    st.cache_data.clear()
    st.info("✅ Cache cleared. Refresh page to reload data.")


# ========================================
# DATA PROCESSING UTILITIES
# ========================================

def aggregate_by_year(df: pd.DataFrame, agg_func: str = 'mean') -> pd.DataFrame:
    """
    Aggregate data by year.
    
    Args:
        df: DataFrame with datetime index
        agg_func: Aggregation function ('mean', 'sum', 'max', 'min')
    
    Returns:
        DataFrame aggregated by year
    """
    if not hasattr(df.index, 'year'):
        return df
    
    return df.groupby(df.index.year).agg(agg_func)


def calculate_moving_average(series: pd.Series, window: int = 30) -> pd.Series:
    """
    Calculate moving average.
    
    Args:
        series: Input series
        window: Window size in years (or periods)
    
    Returns:
        Moving average series
    """
    return series.rolling(window=window, center=True).mean()


def calculate_percentile(data: pd.DataFrame, percentile: float) -> float:
    """
    Calculate percentile across all values in DataFrame.
    """
    all_values = data.values.flatten()
    all_values = all_values[~pd.isna(all_values)]
    return np.percentile(all_values, percentile)


# ========================================
# PLOTTING UTILITIES
# ========================================

def get_scenario_colors() -> Dict[str, str]:
    """Get consistent colors for climate scenarios."""
    return {
        'SSP126': '#2E7D32',  # Green (low emissions)
        'SSP245': '#F57C00',  # Orange (medium emissions)
        'SSP585': '#C62828',  # Red (high emissions)
        'observation': '#424242',  # Gray (observations)
    }


def get_extreme_colors() -> Dict[str, str]:
    """Get colors for extreme types."""
    return {
        'hot': '#E63946',  # Red for hot
        'cold': '#457B9D',  # Blue for cold
        'neutral': '#CCCCCC',  # Gray for neutral
    }


# ========================================
# ERROR HANDLING
# ========================================

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safely divide, returning default if denominator is zero.
    """
    if denominator == 0:
        return default
    return numerator / denominator


def safe_log(value: float, base: float = 10, default: float = 0) -> float:
    """
    Safely calculate logarithm.
    """
    if value <= 0:
        return default
    return np.log(value) / np.log(base)


# ========================================
# MARKDOWN UTILITIES
# ========================================

def alert_box(message: str, alert_type: str = "info") -> None:
    """
    Display formatted alert box.
    
    Args:
        message: Message text
        alert_type: 'info', 'warning', 'error', 'success'
    """
    if alert_type == "info":
        st.info(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    elif alert_type == "success":
        st.success(message)


def metric_section(title: str, metrics: Dict[str, Any], cols: int = 3) -> None:
    """
    Display a section of metrics in columns.
    
    Args:
        title: Section title
        metrics: Dict of {"metric_name": ("value", "help_text", "delta")}
        cols: Number of columns
    """
    st.markdown(f"### {title}")
    
    columns = st.columns(cols)
    metric_items = list(metrics.items())
    
    for i, (label, (value, help_text, delta)) in enumerate(metric_items):
        with columns[i % cols]:
            if delta:
                st.metric(label, value, delta=delta, help=help_text)
            else:
                st.metric(label, value, help=help_text)


# ========================================
# DOCUMENTATION
# ========================================

def show_help_text(section: str) -> None:
    """
    Display contextual help text.
    
    Args:
        section: Help section name
    """
    help_texts = {
        'temperature_extremes': """
        **Temperature Extremes** are days when temperatures exceed (or fall below) 
        a defined threshold. This analysis shows how the frequency of these extremes 
        changes across different climate scenarios.
        """,
        
        'water_cycles': """
        **Water Cycle Analysis** examines changes in precipitation and discharge 
        patterns, which affect water availability and flood/drought risk.
        """,
        
        'climate_scenarios': """
        **SSP126** (low emissions), **SSP245** (medium emissions), and 
        **SSP585** (high emissions) represent different possible futures 
        based on policy choices and societal changes.
        """,
    }
    
    if section in help_texts:
        st.info(help_texts[section])


# ========================================
# EXPORT UTILITIES
# ========================================

def export_to_csv(df: pd.DataFrame, filename: str) -> str:
    """
    Export DataFrame to CSV format (as string).
    """
    return df.to_csv(index=False)


def export_to_excel(df: pd.DataFrame, filename: str) -> bytes:
    """
    Export DataFrame to Excel format (requires openpyxl).
    """
    try:
        import openpyxl
        return df.to_excel(index=False)
    except ImportError:
        st.warning("openpyxl not installed. Use CSV export instead.")
        return export_to_csv(df, filename)


# Add missing import
import numpy as np
