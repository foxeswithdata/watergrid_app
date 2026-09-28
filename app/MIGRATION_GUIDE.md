# Migration Guide: From Jupyter Notebook to Modular Streamlit App

This guide helps you migrate your existing notebook code to the new modular architecture.

## 🎯 Step-by-Step Migration

### Step 1: Identify Your Code Components

In your existing code, identify these sections:

#### For Water Cycles (`watercycles_all.py`):
- ✅ Data loading and preprocessing
- ✅ Configuration parameters
- ✅ Statistical calculations
- ✅ Plotly figure creation
- ✅ Summary tables

#### For Temperature (`maxtemp.ipynb`):
- ✅ Data loading and preprocessing
- ✅ Configuration parameters
- ✅ Percentile calculations
- ✅ Extreme event counting
- ✅ Multiple visualizations (time series, comparison, heatmap)

### Step 2: Migrate Data Loading

**From:** Individual notebook cells
**To:** `data_loader.py` functions

#### Example Migration

**Original notebook code:**
```python
df = pd.read_csv('tmax_combined_G1.csv')
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df.set_index('date', inplace=True)
```

**Migrated to `data_loader.py`:**
```python
@st.cache_data
def load_temperature_data(site: str, gauge: str, config: Dict[str, Any]) -> Dict[str, Any]:
    file_path = DATA_DIR / f"tmax_combined_{gauge}.csv"
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df.set_index('date', inplace=True)
    
    # Process and return
    return {'raw_data': df, 'summary_stats': {...}}
```

### Step 3: Migrate Configuration

**From:** Hardcoded parameters
**To:** Sidebar controls or configuration dictionaries

#### Temperature Analysis Example

**Original notebook:**
```python
ref_start_year = 1961
ref_end_year = 1990
future_start_year = 2071
future_end_year = 2100
months_to_analyze = [1,2,3,4,5,6,7,8,9,10,11,12]
use_fix = True
fix_value = 30.0
comparison_type = 'above'
```

**Migrated to `tab2_temperature.py`:**
```python
def get_temperature_controls():
    with st.sidebar.expander("🌡️ Temperature Analysis Settings"):
        ref_start = st.number_input("Ref. Start Year", value=1961)
        ref_end = st.number_input("Ref. End Year", value=1990)
        # ... more controls ...
        
        return {
            'ref_start': ref_start,
            'ref_end': ref_end,
            # ... etc
        }
```

### Step 4: Migrate Calculations

**From:** Notebook cells with calculations
**To:** `data_loader.py` functions

#### Example: Temperature Extremes Counting

**Original notebook code:**
```python
def compare_to_threshold(data, threshold):
    if comparison_type == 'below':
        return data <= threshold
    else:
        return data >= threshold

extremes_ref = compare_to_threshold(df_ref, threshold).sum()
```

**Migrated to function in `data_loader.py`:**
```python
def load_temperature_data(site: str, gauge: str, config: Dict[str, Any]):
    # ... loading code ...
    
    # Extract config
    comparison_type = config['comparison_type']
    threshold = config['threshold_value']
    
    # Create comparison helper
    def compare_to_threshold(data, threshold):
        if comparison_type == 'below':
            return data <= threshold
        else:
            return data >= threshold
    
    # Calculate extremes
    extremes_ref = compare_to_threshold(df_ref, threshold).sum()
    
    return {
        'extremes_ref': extremes_ref,
        # ... other outputs
    }
```

### Step 5: Migrate Visualizations

**From:** Plotly code in notebook cells
**To:** Functions in `data_loader.py`, displayed in tab files

#### Example: Create a Visualization Function

**Original notebook:**
```python
fig = go.Figure()

for scenario in ssp126_scenarios_filtered:
    fig.add_trace(go.Scatter(
        x=df_all.index,
        y=extremes_all[scenario],
        mode='lines',
        name=scenario,
        line=dict(color='green', width=1)
    ))

fig.update_layout(
    title="Days Above 30°C Over Time",
    xaxis_title="Year",
    yaxis_title="Days",
    hovermode='x unified'
)

fig.show()
```

**Migrated to `data_loader.py`:**
```python
def _create_timeseries_figure(extremes_all, threshold, config):
    """Create time series plot for temperature extremes."""
    fig = go.Figure()
    
    for scenario in extremes_all.columns:
        fig.add_trace(go.Scatter(
            x=extremes_all.index,
            y=extremes_all[scenario],
            mode='lines',
            name=scenario,
            line=dict(width=1)
        ))
    
    fig.update_layout(
        title=f"Days {'Above' if config['comparison_type'] == 'above' else 'Below'} {threshold}°C Over Time",
        xaxis_title="Year",
        yaxis_title="Days",
        hovermode='x unified',
        height=500
    )
    
    return fig
```

**Display in `tab2_temperature.py`:**
```python
if 'timeseries_figure' in data:
    st.plotly_chart(data['timeseries_figure'], use_container_width=True)
```

### Step 6: Migrate Summary Tables

**From:** Printed summaries in notebook
**To:** Streamlit metrics and dataframes

#### Example: Summary Statistics

**Original notebook:**
```python
print(f"Reference period {ref_start_year}-{ref_end_year}: {len(df_ref)} days")
print(f"Mean days/year: {mean_days:.1f}")
```

**Migrated to `tab2_temperature.py`:**
```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Ref. Period - Mean Days/Year",
        f"{stats['ref_mean_days']:.1f}",
        help="Average extreme days per year"
    )
```

## 🔄 Complete Example: Temperature Analysis

Here's how to fully migrate the temperature notebook:

### 1. Update `data_loader.py`

Add this function to handle all temperature processing:

```python
@st.cache_data
def load_temperature_data(site: str, gauge: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Load and process temperature data from notebook."""
    
    # Load CSV
    df = pd.read_csv(DATA_DIR / f"tmax_combined_{gauge}.csv")
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df.set_index('date', inplace=True)
    
    # Extract config
    ref_start = config['ref_start']
    ref_end = config['ref_end']
    future_start = config['future_start']
    future_end = config['future_end']
    months = [int(m.split(":")[0]) for m in config['months']]  # Convert month names to numbers
    use_fix = config['use_fix']
    threshold = config['threshold_value']
    comparison_type = config['comparison_type']
    
    # Filter by time period and months
    period_all = (
        (df.index >= f'{ref_start}-01-01') & 
        (df.index <= f'{future_end}-12-31') & 
        (df.index.month.isin(months))
    )
    df_all = df[period_all]
    
    # Calculate extremes
    def count_extremes_per_year(data):
        years = {}
        for year in data.index.year.unique():
            year_data = data[data.index.year == year]
            if comparison_type == 'below':
                extreme_count = (year_data <= threshold).sum()
            else:
                extreme_count = (year_data >= threshold).sum()
            years[year] = extreme_count
        return pd.DataFrame(years).T
    
    extremes_all = count_extremes_per_year(df_all)
    
    # Create time series figure
    fig_timeseries = go.Figure()
    for scenario in extremes_all.columns[:10]:  # Show first 10 scenarios
        fig_timeseries.add_trace(go.Scatter(
            x=extremes_all.index,
            y=extremes_all[scenario],
            mode='lines',
            name=scenario,
            opacity=0.7
        ))
    
    fig_timeseries.update_layout(
        title=f"Temperature Extremes Over Time",
        xaxis_title="Year",
        yaxis_title="Number of Days",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    # Summary statistics
    ref_mean = extremes_all.iloc[:30].values.mean() if len(extremes_all) >= 30 else 0
    future_mean = extremes_all.iloc[-30:].values.mean() if len(extremes_all) >= 30 else 0
    
    return {
        'timeseries_figure': fig_timeseries,
        'summary_stats': {
            'ref_mean_days': ref_mean,
            'future_mean_days': future_mean,
        },
        'detailed_data': extremes_all
    }
```

### 2. Update `tab2_temperature.py`

Replace visualization functions with calls to your migrated data:

```python
def render_tab2(site: str, gauge: str):
    # Get config from sidebar
    config = get_temperature_controls()
    
    # Load data
    data = load_temperature_data(site, gauge, config)
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Reference Mean Days/Year", 
                 f"{data['summary_stats']['ref_mean_days']:.1f}")
    with col2:
        st.metric("Future Mean Days/Year", 
                 f"{data['summary_stats']['future_mean_days']:.1f}")
    
    # Display figure
    st.plotly_chart(data['timeseries_figure'], use_container_width=True)
```

## 📋 Migration Checklist

- [ ] **Copy data loading code** from notebook to `load_temperature_data()` in `data_loader.py`
- [ ] **Extract configuration parameters** to sidebar in `tab2_temperature.py`
- [ ] **Migrate calculations** to `data_loader.py` functions
- [ ] **Convert visualizations** to Plotly figures and add to return dictionary
- [ ] **Create metric displays** in tab file using `st.metric()`
- [ ] **Test with sample data** by running `streamlit run main_app.py`
- [ ] **Verify site/gauge selection** persists across tabs
- [ ] **Add explanatory text** in `st.expander()` blocks
- [ ] **Test data export** functionality
- [ ] **Document any custom parameters** in README

## 🐛 Common Issues & Solutions

### Issue: Caching Problems
**Problem**: Data looks stale or cached incorrectly
**Solution**: 
```python
# Use cache key if config changes
@st.cache_data(ttl=3600)  # 1 hour cache
def load_temperature_data(site: str, gauge: str, config: Dict):
    # ...
```

Or clear cache:
```bash
streamlit cache clear
```

### Issue: Missing Scenarios
**Problem**: Expected scenario columns not appearing in figure
**Solution**: Check column names in CSV match your filtering logic
```python
print(df.columns)  # Debug: print available columns
```

### Issue: Date Parsing Errors
**Problem**: "Unable to parse date" error
**Solution**: Update date format in `load_temperature_data()`:
```python
# Try multiple formats
for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d']:
    try:
        df['date'] = pd.to_datetime(df['date'], format=fmt)
        break
    except:
        continue
```

### Issue: Sidebar Controls Don't Update
**Problem**: Changing sidebar values doesn't refresh results
**Solution**: Make sure function uses `@st.cache_data` and depends on the config parameter:
```python
@st.cache_data
def load_temperature_data(site: str, gauge: str, config: Dict):
    # Streamlit will re-run when config changes if it's in the function params
```

## 📚 Resources

- **Streamlit Caching**: https://docs.streamlit.io/library/advanced-features/caching
- **Plotly Figures**: https://plotly.com/python/
- **Pandas Date/Time**: https://pandas.pydata.org/docs/user_guide/timeseries.html

## 🎉 Next Steps

After migration:
1. Run `streamlit run main_app.py`
2. Test all site/gauge combinations
3. Verify visualizations display correctly
4. Share with team and gather feedback
5. Iterate on styling and content

Good luck! 🚀
