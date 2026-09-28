"""
Tab 2: Temperature Analysis
============================
Displays temperature extremes analysis with explanatory text.
Adapted from the maxtemp.ipynb Jupyter notebook.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from data_loader import load_temperature_data


def render_tab2a_num_days(df,
                          future_start_year,
                          future_end_year,
                          ref_start_year,
                          ref_end_year,
                          months_to_analyze=None,
                          use_fix=None,
                          threshold_value=None,
                          comparison_type=None
):

    print("Rendering Tab 2a: Number of Extreme Days Over Time")

    # Define temporal resolution ('monthly' or 'daily')
    temporal_resolution = 'daily'  # Options: 'monthly' or 'daily'

    # Define threshold type
    fix_value = threshold_value  # Fixed threshold value (only used if use_fix = True)

    # Define percentile threshold for analysis (only used if use_fix = False)
    percentile_threshold = threshold_value  # e.g., 90 = 90th percentile

    # Define comparison type ('below' for cold extremes, 'above' for hot extremes)
    comparison_type = 'above'  # Options: 'below', 'above'

    # Define scenario exclusion patterns (global)
    # These patterns will be excluded from all SSP analyses
    # if none should be exclude: exclude_patterns = []
    exclude_patterns = ['ISI_UKESM1-0-LL', 'ISI_GFDL-ESM4']

    # Define moving average window size (in years)
    # Used for trend analysis and smoothing of time series data
    ma_window_years = 30  # Moving average window size in years

    # Create dynamic labels and helper variables based on comparison type
    if comparison_type == 'below':
        direction = 'below'
        direction_cap = 'Below'
        operator_symbol = 'â‰¤'
        operator_text = '<='
        flow_type = 'Low'
        extreme_type = 'cold'
    else:  # 'above'
        direction = 'above'
        direction_cap = 'Above'
        operator_symbol = 'â‰¥'
        operator_text = '>='
        flow_type = 'High'
        extreme_type = 'hot'

    # Helper function for threshold comparison
    def compare_to_threshold(data, threshold):
        if comparison_type == 'below':
            return data <= threshold
        else:  # 'above'
            return data >= threshold

    # Create dynamic labels based on temporal resolution
    if temporal_resolution == 'daily':
        period_label = 'day'
        period_label_plural = 'days'
        period_label_cap = 'Day'
        period_label_cap_plural = 'Days'
    else:  # monthly
        period_label = 'month'
        period_label_plural = 'months'
        period_label_cap = 'Month'
        period_label_cap_plural = 'Months'

    # Display configuration
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    month_label = ', '.join([month_names[m] for m in months_to_analyze])

    print(f"Analysis Configuration:")
    print(f"  Reference period: {ref_start_year}-{ref_end_year}")
    print(f"  Future period: {future_start_year}-{future_end_year}")
    print(f"  {period_label_cap_plural}: {month_label} ({months_to_analyze})")
    print(f"  Temporal resolution: {temporal_resolution}")
    if use_fix:
        print(f"  Threshold type: Fixed value = {fix_value}")
    else:
        print(f"  Threshold type: {percentile_threshold}th percentile")
    print(f"  Comparison type: {comparison_type} ({extreme_type} extremes)")
    print(f"  Period duration: {ref_end_year - ref_start_year + 1} years")

    period_ref = (df.index >= f'{ref_start_year}-01-01') & (df.index <= f'{ref_end_year}-12-31') & (
        df.index.month.isin(months_to_analyze))
    period_future = (df.index >= f'{future_start_year}-01-01') & (df.index <= f'{future_end_year}-12-31') & (
        df.index.month.isin(months_to_analyze))
    period_all = (df.index >= f'{ref_start_year}-01-01') & (df.index <= f'{future_end_year}-12-31') & (
        df.index.month.isin(months_to_analyze))

    # Filter data for each period
    df_ref = df[period_ref]
    df_future = df[period_future]
    df_all = df[period_all]
    print(f"Reference period {ref_start_year}-{ref_end_year} ({month_label}): {len(df_ref)} {period_label_plural}")
    print(
        f"Future period {future_start_year}-{future_end_year} ({month_label}): {len(df_future)} {period_label_plural}")
    print(f"All period {ref_start_year}-{future_end_year} ({month_label}): {len(df_all)} {period_label_plural}")

    # Create filtered scenario lists for each SSP
    ssp126_scenarios_filtered = [col for col in df.columns
                                 if 'SSP126' in col and not any(pattern in col for pattern in exclude_patterns)]
    ssp245_scenarios_filtered = [col for col in df.columns
                                 if 'SSP245' in col and not any(pattern in col for pattern in exclude_patterns)]
    ssp370_scenarios_filtered = [col for col in df.columns
                                 if 'SSP370' in col and not any(pattern in col for pattern in exclude_patterns)]
    ssp585_scenarios_filtered = [col for col in df.columns
                                 if 'SSP585' in col and not any(pattern in col for pattern in exclude_patterns)]
    results = []

    # Create column name labels based on configured periods
    ref_label = f'{ref_start_year}_{ref_end_year}'
    future_label = f'{future_start_year}_{future_end_year}'

    # Determine threshold label based on whether using fixed value or percentile
    if use_fix:
        # Use just the value without 'Fixed_' prefix
        threshold_label = f'{fix_value}'
        percentile_label = threshold_label
    else:
        # Convert percentile to quantile (5 -> 0.05)
        quantile_value = percentile_threshold / 100.0
        percentile_label = f'P{percentile_threshold}'
        threshold_label = percentile_label

    for col in df.columns:
        data_ref = df_ref[col]
        data_future = df_future[col]

        # Calculate threshold based on use_fix flag
        if use_fix:
            threshold = fix_value
        else:
            threshold = data_ref.quantile(quantile_value)

        results.append({
            'Scenario': col,
            f'Avg_{ref_label}': data_ref.mean(),
            f'P5_{ref_label}': data_ref.quantile(0.05),
            f'P10_{ref_label}': data_ref.quantile(0.10),
            f'P50_{ref_label}': data_ref.quantile(0.50),
            f'P95_{ref_label}': data_ref.quantile(0.95),
            f'Avg_{future_label}': data_future.mean(),
            f'P5_{future_label}': data_future.quantile(0.05),
            f'P10_{future_label}': data_future.quantile(0.10),
            f'P50_{future_label}': data_future.quantile(0.50),
            f'P95_{future_label}': data_future.quantile(0.95),
            f'{threshold_label}_{ref_label}': threshold,
            f'{period_label_cap}_{direction}_{threshold_label}_{ref_label}': compare_to_threshold(data_ref,
                                                                                                  threshold).sum(),
            f'Pct_{direction}_{threshold_label}_{ref_label}': 100 * compare_to_threshold(data_ref,
                                                                                         threshold).sum() / len(
                data_ref),
            f'{period_label_cap}_{direction}_{threshold_label}_{future_label}': compare_to_threshold(data_future,
                                                                                                     threshold).sum(),
            f'Pct_{direction}_{threshold_label}_{future_label}': 100 * compare_to_threshold(data_future,
                                                                                            threshold).sum() / len(
                data_future)
        })

    results_df = pd.DataFrame(results)

    # Cell No: 7
    # Add SSP classification to results
    results_df['SSP'] = results_df['Scenario'].apply(
        lambda x: 'SSP1-2.6' if 'SSP126' in x else (
            'SSP2-4.5' if 'SSP245' in x else ('SSP3-7.0' if 'SSP370' in x else 'SSP5-8.5'))
    )

    # Calculate period per year
    num_years = future_end_year - future_start_year + 1
    results_df[f'{period_label_cap}_per_year_{future_label}'] = results_df[
                                                                    f'{period_label_cap}_{direction}_{percentile_label}_{future_label}'] / num_years

    # Sort by period per year
    results_sorted = results_df.sort_values(f'{period_label_cap}_per_year_{future_label}', ascending=True)

    fig3 = go.Figure()

    # Add bars with colors by SSP
    # for ssp in ['SSP1-2.6', 'SSP2-4.5', 'SSP3-7.0', 'SSP5-8.5']:
    for ssp in ['SSP1-2.6', 'SSP2-4.5', 'SSP5-8.5']:
        ssp_data = results_sorted[results_sorted['SSP'] == ssp]
        color = 'lightblue' if ssp == 'SSP1-2.6' else (
            'pink' if ssp == 'SSP2-4.5' else ('orange' if ssp == 'SSP3-7.0' else 'red'))
        color = 'lightblue' if ssp == 'SSP1-2.6' else (
            'pink' if ssp == 'SSP2-4.5' else ('orange' if ssp == 'SSP3-7.0' else 'red'))

        fig3.add_trace(go.Bar(
            y=ssp_data['Scenario'],
            x=ssp_data[f'{period_label_cap}_per_year_{future_label}'],
            name=ssp,
            orientation='h',
            marker_color=color,
            text=ssp_data[f'{period_label_cap}_per_year_{future_label}'].round(1),
            textposition='auto',
            texttemplate='%{text}'
        ))

    # Calculate baseline periods per year based on use_fix flag
    num_years_ref = ref_end_year - ref_start_year + 1

    if use_fix:
        # For fixed value: calculate actual count of periods above/below threshold in reference data
        # Take average across all scenarios in reference period
        total_count = 0
        for col in df_ref.columns:
            total_count += compare_to_threshold(df_ref[col], fix_value).sum()
        baseline_periods_per_year = (total_count / len(df_ref.columns)) / num_years_ref
        threshold_display = f'{fix_value}'
    else:
        # For percentile: calculate based on percentile threshold
        num_periods_per_year = len(df_ref) / num_years_ref
        if comparison_type == 'below':
            baseline_periods_per_year = num_periods_per_year * (percentile_threshold / 100.0)
        else:
            baseline_periods_per_year = num_periods_per_year * ((100 - percentile_threshold) / 100.0)
        threshold_display = f'{percentile_threshold}th percentile'

    fig3.add_vline(x=baseline_periods_per_year, line_dash="dash", line_color="green",
                   annotation_text=f"Baseline ({baseline_periods_per_year:.2f} {period_label}/year {direction} {percentile_label})",
                   annotation_position="top right")

    fig3.update_layout(
        title=f'{period_label_cap} per Year {direction_cap} {percentile_label} by Scenario ({future_start_year}-{future_end_year})<br><sub>Threshold: {threshold_display} based on {ref_start_year}-{ref_end_year} ({month_label})</sub>',
        xaxis_title=f'{period_label_cap} per Year',
        yaxis_title='Climate Scenario',
        height=900,
        width=1000,
        barmode='group',
        showlegend=True,
        yaxis=dict(tickfont=dict(size=9))
    )

    return fig3

# ========================================
# CONFIGURATION SIDEBAR (Per-Tab Controls)
# ========================================
def get_temperature_controls():
    """
    Create sidebar controls specific to temperature analysis.
    These don't affect Tab 1 since they're defined here.
    """
    with st.sidebar.expander("🌡️ Temperature Analysis Settings", expanded=True):
        st.markdown("**Analysis Configuration**")
        
        # Time periods
        col1, col2 = st.columns(2)
        with col1:
            ref_start = st.number_input("Ref. Start Year", value=1961, min_value=1961, max_value=2100)
            ref_end = st.number_input("Ref. End Year", value=1990, min_value=1961, max_value=2100)
        
        with col2:
            future_start = st.number_input("Future Start Year", value=2071, min_value=1961, max_value=2100)
            future_end = st.number_input("Future End Year", value=2100, min_value=1961, max_value=2100)
        
        # Months selection
        months = st.multiselect(
            "Months to analyze",
            options=["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            default=["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        )
        
        # Threshold type
        threshold_type = st.radio(
            "Threshold type",
            options=["Fixed value", "Percentile"],
            horizontal=True
        )
        
        if threshold_type == "Fixed value":
            threshold_value = st.number_input("Fixed threshold (°C)", value=30.0, step=0.5)
            use_fix = True
        else:
            threshold_value = st.number_input("Percentile", value=90.0, min_value=0.0, max_value=100.0, step=1.0)
            use_fix = False
        
        # Comparison type
        comparison_type = st.radio(
            "Analysis focus",
            options=["Above (Hot extremes)", "Below (Cold extremes)"],
            horizontal=True
        )

        comparison_type = st.radio(
            "Analysis focus (cold extremes not implemented yet)",
            options=["Above (Hot extremes)"],
            horizontal=True
        )
        comparison_type = "above" if "Above" in comparison_type else "below"
        
        return {
            'ref_start': ref_start,
            'ref_end': ref_end,
            'future_start': future_start,
            'future_end': future_end,
            'months': months,
            'threshold_value': threshold_value,
            'use_fix': use_fix,
            'comparison_type': comparison_type
        }


def render_tab2(site: str, gauge: str):
    """
    Render the Temperature Analysis tab.
    
    Args:
        site: Selected site name
        gauge: Selected gauge/location name
    """
    
    # ========================================
    # INTRODUCTION & EXPLANATION
    # ========================================
    st.markdown("## Temperature Extremes Analysis")
    
    with st.expander("📖 **How to interpret this analysis**", expanded=False):
        st.markdown("""
        ### What is Temperature Extremes Analysis?
        This tab analyzes how extreme temperature events are changing over time,
        comparing historical observations with future climate projections.
        
        ### Key Concepts
        
        **Temperature Extremes:**
        - **Hot extremes**: Days when temperature exceeds a threshold (30°C, 90th percentile, etc.)
        - **Cold extremes**: Days when temperature falls below a threshold
        
        **Climate Scenarios:**
        - **SSP126**: Scenario with strong climate mitigation (1.5-2°C warming by 2100)
        - **SSP245**: Intermediate scenario with current policies (2.5-3°C warming)
        - **SSP585**: High-emissions scenario (3.5-4°C+ warming by 2100)
        
        ### What Changes Across Scenarios?
        As emissions increase from SSP126 → SSP245 → SSP585:
        - **Hotter extremes** → More frequent and more intense
        - **Colder extremes** → Less frequent and less intense
        - The difference between scenarios grows over time
        
        ### How to Read the Graphs
        1. **Time series plot**: Shows the number of extreme days per year (colored lines = different scenarios)
        2. **Moving average**: 30-year smoothing line helps see trends despite year-to-year variability
        3. **Bar charts**: Aggregate counts for reference vs. future periods
        4. **Color scale**: Intensity map showing long-term patterns
        """)
    
    st.markdown("---")
    
    # ========================================
    # GET CONFIGURATION
    # ========================================
    config = get_temperature_controls()
    
    # ========================================
    # LOAD DATA
    # ========================================
    st.markdown("### 📊 Loading Temperature Data...")
    
    try:
        data = load_temperature_data(site, gauge, config)
    except FileNotFoundError:
        st.error(
            f"❌ Temperature data file not found for {site} - {gauge}\n\n"
            "Make sure the temperature CSV files are available in the data directory."
        )
        st.info(
            "Expected file format: `tmax_combined_{gauge}.csv` or similar\n"
            "File should contain date column and scenario columns."
        )
        return
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return
    
    st.success("✅ Data loaded successfully!")
    st.markdown("---")
    

    # ========================================
    # VISUALIZATIONS
    # ========================================
    st.markdown("### 📊 Visualizations")
    
    # Tab 2a: Time Series Analysis
    st_tab2a, st_tab2b = st.tabs([
        "Scenario Comparison",
        "Time Series Analysis"
    ])
    
    with st_tab2a:
        st.markdown("#### Time Series: Extreme Days Over Time")
        with st.expander("📌 **How to read this chart**", expanded=False):
            st.markdown("""...""")

        months_to_analyze = [
            {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}[m[:3]]
            for m in config['months']
        ]

        print("DEBUG 1: About to check if 'timeseries_figure' in data")  # ← ADD THIS
        print(f"DEBUG 2: data keys are: {data.keys()}")  # ← AND THIS

        if 'timeseries_figure' in data:
            print("DEBUG 3: Found timeseries_figure in data")  # ← AND THIS
            fig = render_tab2a_num_days(...)
        else:
            print("DEBUG 4: timeseries_figure NOT in data!")  # ← AND THIS

        fig = render_tab2a_num_days(
                df=data['raw_df'],  # ✅ Pass the actual DataFrame
                future_start_year=config['future_start'],
                future_end_year=config['future_end'],
                ref_start_year=config['ref_start'],
                ref_end_year=config['ref_end'],
                months_to_analyze=months_to_analyze,
                use_fix=config["use_fix"],
                threshold_value=config["threshold_value"],
                comparison_type=config["comparison_type"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with st_tab2b:
        st.markdown("#### Scenario Comparison: Reference vs. Future")
        with st.expander("📌 **How to read this chart**", expanded=False):
            st.markdown("""
            **Comparing Scenarios:**
            - **Bars = Total extreme days** across all years in each period
            - **Three groups** = Three climate scenarios (SSP126, SSP245, SSP585)
            - **Within each group** = Reference period (left) vs. Future period (right)
            
            **What it tells you:**
            - Growing bar heights show increasing extremes
            - SSP585 usually has the largest increase
            - If bars stay the same, extremes aren't changing much
            """)
        
        if 'comparison_figure' in data:
            st.plotly_chart(data['comparison_figure'], use_container_width=True)
        else:
            st.warning("Scenario comparison visualization not available")
    
    # with st_tab2c:
    #     st.markdown("#### Detailed Analysis: Heatmap & Statistics")
    #     with st.expander("📌 **How to read this chart**", expanded=False):
    #         st.markdown("""
    #         **Top panel (Bar width):**
    #         - Total days above threshold in reference and future periods
    #         - Shows absolute counts
    #
    #         **Bottom panel (Color scale):**
    #         - Daily frequency in recent years
    #         - Darker = more days with extremes
    #         - Shows long-term trend over 30-year moving average
    #
    #         **Together they show:**
    #         1. Historical baseline (left side)
    #         2. How frequency is changing (colors)
    #         3. Future projections (right side)
    #         """)
    #
    #     if 'heatmap_figure' in data:
    #         st.plotly_chart(data['heatmap_figure'], use_container_width=True)
    #     else:
    #         st.warning("Detailed analysis visualization not available")
    
    st.markdown("---")
    
    # ========================================
    # KEY INSIGHTS
    # ========================================
    # st.markdown("### 💡 Key Insights")
    #
    # col1, col2 = st.columns(2)
    #
    # with col1:
    #     st.markdown("#### 🔴 Hot Extremes" if config['comparison_type'] == 'above' else "#### 🔵 Cold Extremes")
    #     if 'key_insights' in data:
    #         st.markdown(data['key_insights'].get('extreme_text',
    #             "Examine the trends in the visualizations above."))
    #
    # with col2:
    #     st.markdown("#### 🎯 What This Means for You")
    #     if 'key_insights' in data:
    #         st.markdown("""
    #         **Implications:**
    #         - Infrastructure may need adaptation
    #         - Agricultural practices may require changes
    #         - Water management strategies should evolve
    #         - Emergency preparedness plans need updating
    #         """)
    
    st.markdown("---")
    
    # ========================================
    # DATA EXPORT
    # ========================================
    # st.markdown("### 📥 Export Data")
    #
    # if 'detailed_data' in data:
    #     col1, col2 = st.columns(2)
    #
    #     with col1:
    #         csv = data['detailed_data'].to_csv(index=False)
    #         st.download_button(
    #             label="⬇️ Download Detailed Statistics (CSV)",
    #             data=csv,
    #             file_name=f"temperature_analysis_{site}_{gauge}.csv",
    #             mime="text/csv"
    #         )
    #
    #     with col2:
    #         st.info("💾 Download button is active above")
    #
    # st.markdown("---")
    #
    # ========================================
    # FOOTER NOTES
    # ========================================
    # st.markdown("### 📝 Notes on Interpretation")
    # st.markdown("""
    # - **Model uncertainty**: Different climate models give different results.
    #   The range of projections shows this uncertainty.
    # - **Natural variability**: Year-to-year changes are normal. Look at trends, not individual years.
    # - **Regional differences**: Your location may not follow global average patterns.
    # - **Data quality**: Analysis depends on input data quality. Check source data if available.
    # """)
    
    st.info(
        "💬 **Questions?** Review the interpretation guides (📌) throughout this tab. "
        "Use the sidebar to adjust analysis parameters and see how results change."
    )
