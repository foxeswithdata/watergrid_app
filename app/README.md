# Water Cycles & Temperature Analysis Platform

A modular Streamlit application for analyzing water cycle and climate data across multiple sites with interactive visualizations and explanatory content.

## 📋 Features

- **Modular Architecture**: Separate modules for each tab, making it easy to maintain and extend
- **Persistent Controls**: Site and gauge selection persists across tabs
- **Tab-Specific Settings**: Temperature analysis has its own configuration sidebar
- **Multiple Visualizations**: Time series, scenario comparisons, and detailed analysis charts
- **Explanatory Content**: Built-in guides for interpreting results
- **Data Export**: Download analysis results as CSV files

## 📁 Project Structure

```
project/
├── main_app.py              # Master Streamlit app (entry point)
├── tab1_watercycles.py      # Water cycle analysis tab
├── tab2_temperature.py      # Temperature extremes tab
├── data_loader.py           # Centralized data loading
├── utils.py                 # Shared utility functions
├── data/                    # Data directory (create this)
│   ├── discharge_G1.csv     # Water discharge data
│   ├── tmax_combined_G1.csv # Temperature data
│   └── ...
└── README.md                # This file
```

## 🚀 Getting Started

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install streamlit pandas numpy plotly
```

3. **Create data directory**:
```bash
mkdir data
```

4. **Add your data files**:
   - Place CSV files in the `data/` directory
   - Expected structure:
     - `discharge_G1.csv` (water cycle data)
     - `tmax_combined_G1.csv` (temperature data)
     - Add more gauges as needed (G2, G3, etc.)

### Running the App

```bash
streamlit run main_app.py
```

The app will open at `http://localhost:8501`

## 📊 Data Format

### Water Cycle Data
Expected CSV format with columns:
- `date` - Date column (format: DD/MM/YYYY or YYYY-MM-DD)
- Discharge values for different scenarios/gauges

Example:
```
date,SSP126_scenario1,SSP126_scenario2,SSP245_scenario1,...
01/01/1961,2.3,2.5,2.4,...
...
```

### Temperature Data
Expected CSV format with columns:
- `date` - Date column (format: DD/MM/YYYY or YYYY-MM-DD)
- Temperature values for different scenarios

Example:
```
date,SSP126_scenario1,SSP126_scenario2,SSP245_scenario1,...
01/01/1961,15.2,14.8,15.5,...
...
```

## ⚙️ Configuration

### Adding New Sites

Edit `data_loader.py` and add to `SITES_CONFIG`:

```python
SITES_CONFIG = {
    "Your Site Name": {
        "gauges": ["G1", "G2", "G3"],
        "water_file": "discharge_{gauge}.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    },
    # ... more sites
}
```

### Data Directory Path

If your data is in a different location, update in `data_loader.py`:

```python
DATA_DIR = Path("path/to/your/data")
```

## 📑 Module Overview

### `main_app.py` (Entry Point)
- Page configuration
- Sidebar controls (persistent site/gauge selection)
- Tab layout management
- Footer

### `tab1_watercycles.py` (Water Cycles Tab)
- Water cycle visualization and analysis
- Explanatory sections
- Summary statistics
- Data export functionality

**To implement:**
1. Load your current `watercycles_all.py` logic
2. Modify `load_watercycles_data()` in `data_loader.py` to process your data
3. Create visualization functions in `data_loader.py`
4. Update the `render_tab1()` function to use your visualizations

### `tab2_temperature.py` (Temperature Tab)
- Temperature extremes analysis
- Configuration sidebar for analysis parameters
- Multiple visualization tabs
- Scenario comparison

**To implement:**
1. Replace placeholder figures in `load_temperature_data()`
2. Copy visualization code from `maxtemp.ipynb`
3. Update configuration controls as needed

### `data_loader.py` (Shared Data Loading)
- Centralized data I/O
- Caching with `@st.cache_data`
- Data validation
- Site/gauge management

**To customize:**
1. Update file path patterns based on your naming convention
2. Adjust CSV column names to match your data
3. Implement actual visualization functions

### `utils.py` (Utilities)
- Formatting functions
- Validation functions
- Calculation helpers
- Export utilities

## 🎨 Customization Guide

### Change Colors & Styling

Update scenario colors in `utils.py`:
```python
def get_scenario_colors() -> Dict[str, str]:
    return {
        'SSP126': '#2E7D32',  # Green
        'SSP245': '#F57C00',  # Orange
        'SSP585': '#C62828',  # Red
    }
```

### Modify Tab Titles

In `main_app.py`, edit the tab labels:
```python
tab1, tab2 = st.tabs([
    "💧 Custom Tab 1 Title",
    "🌡️ Custom Tab 2 Title"
])
```

### Adjust Explanatory Content

Each tab's explanatory text is in `st.expander()` blocks. Edit the markdown directly in:
- `tab1_watercycles.py`
- `tab2_temperature.py`

## 📈 Adding More Tabs

1. Create `tab3_newanalysis.py`:
```python
def render_tab3(site: str, gauge: str):
    st.markdown("## My New Analysis")
    # Your content here
```

2. Update `main_app.py`:
```python
from tab3_newanalysis import render_tab3

tab1, tab2, tab3 = st.tabs([
    "💧 Water Cycles",
    "🌡️ Temperature",
    "📊 New Analysis"
])

with tab3:
    render_tab3(selected_site, selected_gauge)
```

3. Add data loading function to `data_loader.py`:
```python
@st.cache_data
def load_newanalysis_data(site: str, gauge: str):
    # Your data loading logic
    return {...}
```

## 🔍 Troubleshooting

### Issue: "File not found" error
- **Solution**: Check that data files are in the correct directory and filename matches the pattern in `SITES_CONFIG`

### Issue: "No 'date' column found"
- **Solution**: Ensure CSV files have a 'date' column; update date parsing in `data_loader.py` if format differs

### Issue: Data not updating
- **Solution**: Clear cache by running:
```bash
streamlit cache clear
```
Or in your Python script:
```python
from utils import clear_cache
clear_cache()
```

### Issue: Tab selection doesn't persist between reruns
- **Solution**: Streamlit reruns the entire script when you interact with widgets. Use `st.session_state` (already done in sidebar) to maintain state.

## 📦 Dependencies

- **streamlit** >= 1.0 - Web app framework
- **pandas** >= 1.0 - Data manipulation
- **numpy** >= 1.19 - Numerical computing
- **plotly** >= 5.0 - Interactive visualizations

Install with:
```bash
pip install streamlit pandas numpy plotly
```

## 🎓 Converting from Jupyter Notebook

To migrate visualization code from your Jupyter notebook:

1. **Identify visualization cells**:
   - Copy Plotly figure creation code
   - Move to `data_loader.py` as visualization functions

2. **Convert to functions**:
   ```python
   def create_main_figure(df, config):
       fig = go.Figure()
       # Your plotting code
       return fig
   ```

3. **Integrate into tab**:
   ```python
   if 'main_figure' in data:
       st.plotly_chart(data['main_figure'], use_container_width=True)
   ```

## 🤝 Extending the App

### Add a New Gauge
1. Update `SITES_CONFIG` in `data_loader.py`
2. Add corresponding CSV files to `data/` directory
3. Restart the app - new gauge will appear automatically

### Add a Custom Metric
1. Create calculation function in `utils.py`
2. Call from tab file:
   ```python
   from utils import calculate_percentile
   ```

### Add Configuration Options
1. Add to sidebar in `tab2_temperature.py` (or create similar for other tabs)
2. Pass to data loading function
3. Use in calculations and visualizations

## 📝 Example: Migrating Your Current App

If you already have `watercycles_all.py`:

1. **Copy your visualization code** into `data_loader.py`:
```python
def load_watercycles_data(site: str, gauge: str) -> Dict[str, Any]:
    # ... existing loading code ...
    
    # Your existing figure creation code
    main_fig = go.Figure()
    # ... add traces and layout ...
    
    return {
        'main_figure': main_fig,
        'scenario_figure': scenario_fig,
        'extremes_figure': extremes_fig,
        'summary_stats': {...},
        'data_table': df,
    }
```

2. **Keep your sidebar dropdowns** - they're already in `main_app.py`

3. **Test with your data** and iterate on styling

## 📞 Support

For issues:
1. Check the Troubleshooting section above
2. Review Streamlit documentation: https://docs.streamlit.io/
3. Check Plotly examples: https://plotly.com/python/

## 📄 License

Adapt as needed for your organization.

---

**Happy analyzing! 🎉**
