"""
Master Streamlit Application: Water Cycles & Temperature Analysis
=================================================================
Main entry point for the application. Handles:
- Site and location/gauge selection (persistent across tabs)
- Tab navigation
- Page configuration and styling
"""

import streamlit as st
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from data_loader import get_gauge_names_for_site
from data_loader import get_sites, get_gauges_for_site
from tab1_watercycles import render_tab1
from tab2_temperature import render_tab2

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="WaterGrid Catchment and Climate Analysis",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# SIDEBAR - PERSISTENT CONTROLS
# ========================================
st.sidebar.markdown("## **Configuration**")
st.sidebar.markdown("---")

# Initialize session state for persistence
if 'selected_site' not in st.session_state:
    st.session_state.selected_site = None
if 'selected_gauge' not in st.session_state:
    st.session_state.selected_gauge = None

# Load available sites
sites = get_sites()

# Site selector
selected_site = st.sidebar.selectbox(
    "📍 Select Site:",
    options=sites,
    key='site_selector',
    help="Choose a site to analyze"
)

st.session_state.selected_site = selected_site

# Gauge/Location selector (depends on site selection)
if selected_site:
    gauges = get_gauges_for_site(selected_site)
    gauge_names = get_gauge_names_for_site(selected_site)
    selected_gauge = st.sidebar.selectbox(
        "📊 Select Location:",
        options=gauge_names,
        key='gauge_selector',
        help="Choose a specific gauge or monitoring location"
    )
    ### assign value from selected gauge to be in gauges from index in gauge_names
    if selected_gauge in gauge_names:
        selected_gauge_idx = gauge_names.index(selected_gauge)
        selected_gauge = gauges[selected_gauge_idx]
    st.session_state.selected_gauge = selected_gauge
else:
    selected_gauge = None
    st.session_state.selected_gauge = None

st.sidebar.markdown("---")
st.sidebar.markdown("### **About**")
st.sidebar.info(
    "This application analyzes water cycles and climate extremes across "
    "Watergrid sites and climate change scenarios. Select a site and gauge"
    "to begin."
)

# ========================================
# MAIN CONTENT - HEADER
# ========================================
st.title("Watergrid Catchment Level Modelling and Climate Analysis")

if selected_site and selected_gauge:
    st.markdown(f"**Site:** {selected_site} | **Location:** {selected_gauge}")
else:
    st.warning("⚠️ Please select a site and gauge from the sidebar to continue.")
    st.stop()

st.markdown("---")

# ========================================
# TABS
# ========================================
tab1, tab2 = st.tabs([
    "💧 Water Cycles Analysis",
    "🌡️ Temperature Analysis"
])

with tab1:
    render_tab1(selected_site, selected_gauge)

with tab2:
    render_tab2(selected_site, selected_gauge)

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "Watergrid Catchment Level Modelling and Climate Analysis | IIASA Biodiversity and Natural Resources Program<br>"
    f"Site: {selected_site} | Gauge: {selected_gauge}"
    "</div>",
    unsafe_allow_html=True
)
