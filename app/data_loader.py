"""
Data Loader Module
==================
Centralized data loading for all tabs.
Handles file I/O, data validation, and preprocessing.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Any
import streamlit as st

from date_converter import load_csv_with_date_conversion
from temp_converter import standardize_temperature_column



# ========================================
# CONFIGURATION
# ========================================

# Adjust these paths to match your actual data directory structure
DATA_DIR = Path(__file__).parent / "data_public"  # Change this to your actual data directory
SITES_CONFIG = {
    # Format: "Site Name": {"gauges": ["Gauge1", "Gauge2"], "data_prefix": "file_prefix"}
    "Tamar": {
        "site_name": "Tamar",
        "gauges": ["G1"],
        "gauges_names": ["Gauge 1"],
        "watercycle_file": "balance_average.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    },
    "Averbode": {
        "site_name": "Averbode",
        "gauges": ["G1", "G2"],
        "gauges_names": ["Gauge 1", "Gauge 2"],
        "watercycle_file": "balance_average.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    },
    "Slovakia": {
        "site_name": "Slovakia Bioclimatic Park",
        "gauges": ["G1", "G2"],
        "gauges_names": ["Bioklimatic Park", "Rajec"],
        "watercycle_file": "balance_average.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    },
    "Valencia": {
        "site_name": "Valencia",
        "gauges": ["G1"],
        "gauges_names": ["Gauge 1"],
        "watercycle_file": "balance_average.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    },
    "Malta": {
        "site_name": "Malta",
        "gauges": ["G1", "G2"],
        "gauges_names": ["Gauge 1", "Gauge 2"],
        "watercycle_file": "balance_average.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    }
}

CATEGORY_COLORS = {
    "white": "white",
    "positive": "lightsteelblue",   # Inputs
    "negative": "chocolate",        # Outputs
    "storage": "#00CC96",           # Storage (parent)
    "storpos": "#33AC86",           # Storage pos.
    "storneg": "#539C66",           # Storage neg.
}


# ========================================
# SITE & GAUGE MANAGEMENT
# ========================================

def get_sites() -> List[str]:
    """Get list of available sites."""
    return list(SITES_CONFIG.keys())


def get_gauges_for_site(site: str) -> List[str]:
    """Get available gauges for a specific site."""
    if site in SITES_CONFIG:
        return SITES_CONFIG[site]["gauges"]
    return []

def get_gauge_names_for_site(site: str) -> List[str]:
    """Get names of available gauges for a specific site."""
    if site in SITES_CONFIG:
        return SITES_CONFIG[site]["gauges_names"]
    return []

def _split_row(line: str):
    """Split a CSV line, dropping only the trailing empty cell created by
    the writer's trailing comma (not internal empty cells, which are
    meaningful — e.g. the root label's empty parent)."""
    row = line.split(",")
    if row and row[-1] == "":
        row = row[:-1]
    return row


# ========================================
# WATER CYCLE DATA LOADING
# ========================================

@st.cache_data
def load_watercycles_data(site: str, gauge: str) -> Dict[str, Any]:
    """
    Load water cycle data for a specific site and gauge.
    """
    
    if site not in SITES_CONFIG:
        raise ValueError(f"Site '{site}' not found in configuration")
    
    config = SITES_CONFIG[site]
    
    # Build file path
    water_file = config["watercycle_file"]
    filepath = DATA_DIR / site / water_file
    
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    # Load data
    with open(filepath) as f:
        raw_lines = [line.strip("\n") for line in f.readlines()]

    colors1, parents, labels = None, None, None
    values_out = {}

    for line in raw_lines:
        if not line.strip():
            continue
        row = _split_row(line)
        tag, rest = row[0], row[1:]

        if tag == "colors:":
            colors1 = rest
        elif tag == "parents:":
            parents = rest
        elif tag == "labels:":
            labels = rest
        elif tag.startswith("Storing water balance"):
            continue
        else:
            # A data row: tag is the year (or "Average")
            values_out[tag] = [float(v) for v in rest]

    if colors1 is None or parents is None or labels is None:
        raise ValueError(f"Could not parse expected header rows in {filepath}")

    # Add an overall average across years if the file doesn't already have one
    if "Average" not in values_out and values_out:
        arr = np.array(list(values_out.values()))
        values_out["Average"] = arr.mean(axis=0).tolist()

    colors = [CATEGORY_COLORS.get(c, "#888888") for c in colors1]

    return labels, parents, colors, values_out
    



# ========================================
# TEMPERATURE DATA LOADING
# ========================================

@st.cache_data
def load_temperature_data(site: str, gauge: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load and process temperature data from the notebook.
    
    Args:
        site: Site name
        gauge: Gauge/location name
        config: Configuration dictionary with analysis parameters
    
    Returns:
        Dictionary containing figures, statistics, and data
    """
    
    if site not in SITES_CONFIG:
        raise ValueError(f"Site '{site}' not found in configuration")
    
    site_config = SITES_CONFIG[site]
    
    # Build file path
    temp_file = site_config["temp_file"].format(gauge=gauge)
    file_path = DATA_DIR / site / temp_file

    st.markdown(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Temperature data file not found: {file_path}")
    
    # ========================================
    # LOAD AND PREPARE DATA
    # ========================================
    df = load_csv_with_date_conversion(file_path, to_datetime=True)
    # df = pd.read_csv(file_path)

    print(df.head())

    df.set_index('date', inplace=True)

    for col in df.columns:
        if col != 'date':  # Skip date column
            df = standardize_temperature_column(df, col)

    # Extract configuration
    ref_start_year = config['ref_start']
    ref_end_year = config['ref_end']
    future_start_year = config['future_start']
    future_end_year = config['future_end']
    months_to_analyze = [
        {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
         "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}[m[:3]]
        for m in config['months']
    ]
    use_fix = config['use_fix']
    threshold_value = config['threshold_value']
    comparison_type = config['comparison_type']
    
    # Create comparison helper
    def compare_to_threshold(data, threshold):
        if comparison_type == 'below':
            return data <= threshold
        else:
            return data >= threshold
    
    # ========================================
    # FILTER DATA BY TIME PERIODS
    # ========================================
    
    period_ref = (df.index >= f'{ref_start_year}-01-01') & \
                 (df.index <= f'{ref_end_year}-12-31') & \
                 (df.index.month.isin(months_to_analyze))
    
    period_future = (df.index >= f'{future_start_year}-01-01') & \
                    (df.index <= f'{future_end_year}-12-31') & \
                    (df.index.month.isin(months_to_analyze))
    
    period_all = (df.index >= f'{ref_start_year}-01-01') & \
                 (df.index <= f'{future_end_year}-12-31') & \
                 (df.index.month.isin(months_to_analyze))
    
    df_ref = df[period_ref]
    df_future = df[period_future]
    df_all = df[period_all]
    
    # ========================================
    # CALCULATE STATISTICS
    # ========================================
    
    # Get threshold value for analysis
    if use_fix:
        threshold = threshold_value
    else:
        # Calculate percentile from reference period
        all_scenario_values = df_ref.iloc[:, :].values.flatten()
        all_scenario_values = all_scenario_values[~np.isnan(all_scenario_values)]
        threshold = np.percentile(all_scenario_values, threshold_value)
    
    # Count extreme days for each scenario
    def count_extremes(data, threshold):
        """Count days meeting threshold condition per year"""
        if data.empty:
            return pd.Series()
        
        years_data = {}
        for year in data.index.year.unique():
            year_data = data[data.index.year == year]
            extreme_days = compare_to_threshold(year_data, threshold).sum(axis=0)
            years_data[year] = extreme_days
        
        return pd.DataFrame(years_data).T
    
    # Calculate for each period
    extremes_ref = count_extremes(df_ref, threshold)
    extremes_future = count_extremes(df_future, threshold)
    extremes_all = count_extremes(df_all, threshold)
    
    # Summary statistics
    summary_stats = {
        'ref_mean_days': extremes_ref.values.flatten().mean() if not extremes_ref.empty else 0,
        'future_mean_days': extremes_future.values.flatten().mean() if not extremes_future.empty else 0,
    }
    
    # ========================================
    # CREATE VISUALIZATIONS
    # ========================================
    
    output = {
        'summary_stats': summary_stats,
        'detailed_data': pd.DataFrame({
            'Period': ['Reference', 'Future'],
            'Mean Days/Year': [summary_stats['ref_mean_days'], summary_stats['future_mean_days']],
            'Total Days': [extremes_ref.values.flatten().sum(), extremes_future.values.flatten().sum()]
        }),
        'key_insights': {
            'extreme_text': (
                f"The {'hot' if comparison_type == 'above' else 'cold'} extreme days threshold "
                f"shows a {('increasing' if summary_stats['future_mean_days'] > summary_stats['ref_mean_days'] else 'decreasing')} trend "
                f"from {summary_stats['ref_mean_days']:.1f} to {summary_stats['future_mean_days']:.1f} days/year."
            )
        }
    }
    
    # Add placeholder figures (implement actual visualization code)
    # output['timeseries_figure'] = _create_timeseries_figure(extremes_all, threshold)
    # output['comparison_figure'] = _create_comparison_figure(extremes_ref, extremes_future, threshold)
    # output['heatmap_figure'] = _create_heatmap_figure(extremes_all, threshold)

    return {
        'raw_df': df,  # ✅ ADD THIS
        'output': output
        # ... other stuff
    }


# ========================================
# VISUALIZATION HELPERS (Template)
# ========================================

def _create_timeseries_figure(data, threshold):
    """Create time series plot for temperature extremes."""
    # Implement based on your notebook's visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=[0], name="Placeholder"))
    return fig


def _create_comparison_figure(ref_data, future_data, threshold):
    """Create scenario comparison bar chart."""
    # Implement based on your notebook's visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[0], name="Placeholder"))
    return fig


def _create_heatmap_figure(data, threshold):
    """Create heatmap for detailed analysis."""
    # Implement based on your notebook's visualization
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=[[0]]))
    return fig


# ========================================
# UTILITY FUNCTIONS
# ========================================

def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate that data has required structure.
    """
    required_columns = ['date']
    
    if 'date' in df.columns or df.index.name == 'date':
        return True
    
    return False


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for a dataset.
    """
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'date_range': f"{df.index.min()} to {df.index.max()}" if df.index.name == 'date' else "Unknown",
        'missing_values': df.isnull().sum().sum()
    }
