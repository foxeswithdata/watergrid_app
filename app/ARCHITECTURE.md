# Architecture & Data Flow

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT APPLICATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    main_app.py                           │   │
│  │  - Page Configuration                                   │   │
│  │  - Browser & Tab Management                            │   │
│  │  - Session State Management                            │   │
│  └──────────────┬───────────────────────┬──────────────────┘   │
│                 │                       │                       │
│  ┌──────────────▼──────────┐  ┌────────▼──────────────────┐   │
│  │   SIDEBAR (Persistent)  │  │   MAIN CONTENT            │   │
│  ├─────────────────────────┤  ├──────────────────────────┤   │
│  │ 📍 Site Selector        │  │  [Tab 1] [Tab 2]         │   │
│  │ 📊 Gauge Selector       │  │                          │   │
│  │                         │  │  ┌────────────────────┐  │   │
│  │ (Preserved across tabs) │  │  │ Water Cycles Tab   │  │   │
│  │                         │  │  ├────────────────────┤  │   │
│  │ 🌡️ Temperature Settings │  │  │ • Intro text       │  │   │
│  │ (Only in Tab 2)         │  │  │ • Metrics          │  │   │
│  │                         │  │  │ • Visualizations   │  │   │
│  │                         │  │  │ • Data table       │  │   │
│  │                         │  │  └────────────────────┘  │   │
│  │                         │  │                          │   │
│  │                         │  │  ┌────────────────────┐  │   │
│  │                         │  │  │ Temperature Tab    │  │   │
│  │                         │  │  ├────────────────────┤  │   │
│  │                         │  │  │ • Intro text       │  │   │
│  │                         │  │  │ • Config controls  │  │   │
│  │                         │  │  │ • Sub-tabs:        │  │   │
│  │                         │  │  │   ├─ Time Series   │  │   │
│  │                         │  │  │   ├─ Comparison    │  │   │
│  │                         │  │  │   └─ Detailed      │  │   │
│  │                         │  │  │ • Data export      │  │   │
│  │                         │  │  └────────────────────┘  │   │
│  │                         │  │                          │   │
│  └─────────────────────────┘  └──────────────────────────┘   │
│                 │                       │                       │
│                 └───────────┬───────────┘                       │
│                             │                                   │
│                    ┌────────▼──────────────┐                   │
│                    │   data_loader.py      │                   │
│                    │  (Cached Data Layer)  │                   │
│                    ├───────────────────────┤                   │
│                    │ load_watercycles_data │                   │
│                    │ load_temperature_data │                   │
│                    │ get_sites()           │                   │
│                    │ get_gauges_for_site() │                   │
│                    └────────┬──────────────┘                   │
│                             │                                   │
│                    ┌────────▼──────────────┐                   │
│                    │    utils.py            │                   │
│                    │ (Utility Functions)    │                   │
│                    ├───────────────────────┤                   │
│                    │ format_*()             │                   │
│                    │ validate_*()           │                   │
│                    │ get_*_colors()         │                   │
│                    │ calculate_*()          │                   │
│                    └────────┬──────────────┘                   │
│                             │                                   │
│                    ┌────────▼──────────────┐                   │
│                    │    data/ (CSV files)   │                   │
│                    │                       │                   │
│                    │ discharge_G1.csv      │                   │
│                    │ discharge_G2.csv      │                   │
│                    │ tmax_combined_G1.csv  │                   │
│                    │ tmax_combined_G2.csv  │                   │
│                    └───────────────────────┘                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
USER INTERACTION
    ↓
    ├─→ Select Site (Sidebar)
    │   ├─→ Calls get_sites()
    │   ├─→ Stores in session_state.selected_site
    │   └─→ Updates gauge selector
    │
    ├─→ Select Gauge (Sidebar)
    │   ├─→ Calls get_gauges_for_site()
    │   ├─→ Stores in session_state.selected_gauge
    │   └─→ Passes to active tab
    │
    └─→ Select Tab
        │
        ├─→ TAB 1 (Water Cycles)
        │   ├─→ render_tab1(site, gauge)
        │   ├─→ load_watercycles_data(site, gauge)
        │   │   ├─→ Read: data/discharge_{gauge}.csv
        │   │   ├─→ Process: Filter, aggregate, calculate stats
        │   │   ├─→ Return: dict with figures & data
        │   │   └─→ Cache results for performance
        │   ├─→ Display metrics with st.metric()
        │   ├─→ Display figures with st.plotly_chart()
        │   └─→ Provide CSV download
        │
        └─→ TAB 2 (Temperature)
            ├─→ get_temperature_controls()
            │   ├─→ Reference period (sidebar)
            │   ├─→ Future period (sidebar)
            │   ├─→ Months selection (sidebar)
            │   ├─→ Threshold configuration (sidebar)
            │   └─→ Return config dict
            │
            ├─→ render_tab2(site, gauge)
            ├─→ load_temperature_data(site, gauge, config)
            │   ├─→ Read: data/tmax_combined_{gauge}.csv
            │   ├─→ Parse dates
            │   ├─→ Filter by periods & months
            │   ├─→ Calculate extremes (>= or <= threshold)
            │   ├─→ Create visualizations:
            │   │   ├─ Time series figure
            │   │   ├─ Scenario comparison
            │   │   └─ Heatmap/detailed analysis
            │   ├─→ Calculate statistics
            │   ├─→ Return: dict with all outputs
            │   └─→ Cache results (key: config hash)
            │
            ├─→ Display summary metrics
            ├─→ Sub-tabs for different analyses
            ├─→ Display interpretive guides
            └─→ Provide CSV download
```

## Module Interaction Diagram

```
main_app.py
├─ Imports from: tab1_watercycles, tab2_temperature
├─ Imports from: data_loader, utils
├─ Manages: Session state, tab navigation
└─ Calls:
   ├─ render_tab1(site, gauge) →
   │  └─→ Calls from tab1_watercycles.py
   │     └─→ Imports: data_loader.load_watercycles_data()
   │        └─→ Calls from data_loader.py
   │           ├─→ Read CSV files
   │           ├─→ Calls utils functions for formatting
   │           └─→ Return processed data
   │
   └─ render_tab2(site, gauge) →
      └─→ Calls from tab2_temperature.py
         ├─→ get_temperature_controls() - gets config from sidebar
         ├─→ load_temperature_data(site, gauge, config)
         │  └─→ Calls from data_loader.py
         │     ├─→ Read CSV files
         │     ├─→ Filter and process data
         │     ├─→ Calculate statistics
         │     ├─→ Create Plotly figures
         │     └─→ Return complete output dict
         └─→ Calls utils functions for formatting/validation
```

## File Dependencies

```
main_app.py (Entry point)
├─ IMPORTS:
│  ├─ streamlit
│  ├─ pandas, numpy
│  ├─ tab1_watercycles (render_tab1)
│  ├─ tab2_temperature (render_tab2)
│  └─ data_loader (load_all_data, get_sites, get_gauges_for_site)
│
├─ CALLS:
│  ├─ render_tab1(site, gauge)
│  ├─ render_tab2(site, gauge)
│  ├─ get_sites()
│  └─ get_gauges_for_site(site)
│
└─ SESSION STATE KEYS:
   ├─ selected_site
   └─ selected_gauge

tab1_watercycles.py
├─ IMPORTS:
│  ├─ streamlit
│  ├─ pandas, numpy
│  ├─ plotly
│  └─ data_loader (load_watercycles_data)
│
├─ EXPORTS:
│  └─ render_tab1(site, gauge)
│
└─ CALLS:
   └─ load_watercycles_data(site, gauge)

tab2_temperature.py
├─ IMPORTS:
│  ├─ streamlit
│  ├─ pandas, numpy
│  ├─ plotly
│  └─ data_loader (load_temperature_data)
│
├─ EXPORTS:
│  ├─ render_tab2(site, gauge)
│  └─ get_temperature_controls() [internal]
│
└─ CALLS:
   └─ load_temperature_data(site, gauge, config)

data_loader.py
├─ IMPORTS:
│  ├─ pandas, numpy
│  ├─ plotly
│  └─ streamlit (@st.cache_data)
│
├─ EXPORTS:
│  ├─ get_sites()
│  ├─ get_gauges_for_site(site)
│  ├─ load_watercycles_data(site, gauge) [@st.cache_data]
│  ├─ load_temperature_data(site, gauge, config) [@st.cache_data]
│  └─ validate_data(df)
│
├─ CONFIGURATION:
│  └─ SITES_CONFIG dict
│
└─ FILE ACCESS:
   └─ DATA_DIR / *.csv files

utils.py
├─ IMPORTS:
│  ├─ streamlit
│  ├─ pandas, numpy
│  └─ typing
│
├─ EXPORTS:
│  ├─ format_temperature(value)
│  ├─ format_discharge(value)
│  ├─ validate_year_range(start, end)
│  ├─ validate_months(months)
│  ├─ get_scenario_colors()
│  ├─ get_extreme_colors()
│  ├─ calculate_moving_average(series)
│  ├─ export_to_csv(df)
│  └─ [More utility functions]
│
└─ USED BY:
   ├─ tab1_watercycles (formatting, colors)
   ├─ tab2_temperature (validation, formatting)
   └─ data_loader (calculations, validation)
```

## Session State Management

```
STREAMLIT RERUNS (on widget interaction)
    ↓
ENTIRE SCRIPT RUNS AGAIN
    ↓
Session state persists
    │
    ├─ st.session_state.selected_site
    │  ├─ Set by: st.sidebar.selectbox(key='site_selector')
    │  ├─ Used by: tab rendering functions
    │  └─ Persists across: Tab changes
    │
    ├─ st.session_state.selected_gauge
    │  ├─ Set by: st.sidebar.selectbox(key='gauge_selector')
    │  ├─ Used by: tab rendering functions
    │  └─ Persists across: Tab changes
    │
    └─ [Other user-specific state]
       └─ Can be added as needed
```

## Caching Strategy

```
@st.cache_data decorators on:

1. load_watercycles_data(site, gauge)
   ├─ Cache key: (site, gauge)
   ├─ Invalidates when: site or gauge changes
   └─ Benefit: Avoid reloading CSV on reruns

2. load_temperature_data(site, gauge, config)
   ├─ Cache key: (site, gauge, config dict)
   ├─ Invalidates when: site, gauge, or config changes
   └─ Benefit: Avoid recalculation when config changes

IMPORTANT: Changes to config MUST re-run load_temperature_data()
→ Pass config as parameter (it's part of cache key)
```

## Data Format Flow

```
RAW CSV FILES
    ↓
date,SSP126_scen1,SSP126_scen2,SSP245_scen1,...
01/01/1961,value1,value2,value3,...
02/01/1961,value1,value2,value3,...
    ↓
PANDAS DATAFRAME (in memory)
    ├─ Index: datetime (date column)
    ├─ Columns: scenario names
    └─ Values: measurements
    ↓
PROCESSING
    ├─ Filter by date range (ref period vs future period)
    ├─ Filter by months (e.g., JJA for summer)
    ├─ Calculate per-year statistics
    ├─ Calculate percentiles
    ├─ Count extremes (above/below threshold)
    ├─ Create visualizations
    └─ Generate summary statistics
    ↓
OUTPUT DICTIONARY
    ├─ Plotly figures (for st.plotly_chart)
    ├─ Summary statistics (for st.metric)
    ├─ Data tables (for st.dataframe)
    └─ Other derived data
    ↓
STREAMLIT DISPLAY
    ├─ Figures render interactively
    ├─ Metrics show in cards
    ├─ Tables are filterable/sortable
    └─ Everything is responsive
```

## Performance Optimization

```
STREAMLIT RERUNS (on every interaction)
    ↓
Does data need to load?
    ├─ NO → Use @st.cache_data
    │  └─→ Cached result returned instantly
    │
    └─ YES (site/gauge/config changed) → Load new data
       ├─→ Read CSV from disk (~10-100ms)
       ├─→ Process in pandas (~100-500ms)
       ├─→ Create figures (~100-200ms)
       ├─→ Return and cache (~10ms)
       └─→ Display in Streamlit (~50ms)

TOTAL TIME:
- First load: ~500-1000ms
- Subsequent loads: ~10ms (cached)
- After config change: ~500-1000ms (recalculates)
```

## Error Handling Flow

```
USER ACTION
    ↓
TRY:
├─ Load data file
├─ Validate date column
├─ Validate data columns
├─ Calculate statistics
├─ Create figures
│
CATCH EXCEPTION:
├─ FileNotFoundError
│  └─→ st.error("File not found")
│
├─ ValueError
│  └─→ st.error("Invalid data format")
│
├─ KeyError (missing column)
│  └─→ st.error("Missing required column")
│
└─ Generic Exception
   └─→ st.error("Unexpected error")

FINALLY:
└─→ User sees helpful error message
    with suggestions for fixing
```

## Directory Structure

```
project/
│
├── main_app.py                    # Entry point (285 lines)
├── tab1_watercycles.py           # Tab 1 implementation (225 lines)
├── tab2_temperature.py           # Tab 2 implementation (380 lines)
├── data_loader.py                # Data loading module (320 lines)
├── utils.py                      # Utilities module (260 lines)
│
├── data/                         # Data directory
│   ├── discharge_G1.csv          # Water cycle data for G1
│   ├── discharge_G2.csv          # Water cycle data for G2
│   ├── tmax_combined_G1.csv      # Temperature data for G1
│   ├── tmax_combined_G2.csv      # Temperature data for G2
│   └── [more files as needed]
│
├── README.md                     # Full documentation
├── QUICKSTART.md                 # 5-minute setup
├── MIGRATION_GUIDE.md            # How to migrate notebook code
├── ARCHITECTURE.md               # This file
└── SETUP_SUMMARY.md             # Setup overview
```

## Typical User Workflow

```
1. LAUNCH APP
   streamlit run main_app.py
   └─→ Page loads with default site/gauge

2. SELECT SITE
   └─→ Site dropdown changed
      └─→ Streamlit reruns
         └─→ Gauge selector updates
            └─→ Tab 1 shows "Select site and gauge"
            └─→ Tab 2 shows "Select site and gauge"

3. SELECT GAUGE
   └─→ Gauge dropdown changed
      └─→ Streamlit reruns
         └─→ load_watercycles_data() called
         └─→ load_temperature_data() called (if in Tab 2)
            └─→ Data cached and displayed

4. CLICK TAB 1
   └─→ Tab indicator changes
      └─→ Streamlit reruns (minor)
         └─→ Tab 1 renders with cached data

5. ADJUST TEMP CONFIG
   └─→ Config sidebar value changed
      └─→ Streamlit reruns (if on Tab 2)
         └─→ New config dict created
         └─→ Cache invalidated (new key)
         └─→ load_temperature_data() recalculates
            └─→ New figures generated
            └─→ Results cached with new key
            └─→ Tab 2 displays updated results

6. DOWNLOAD DATA
   └─→ Download button clicked
      └─→ CSV file generated on-the-fly
         └─→ Browser downloads file

7. SWITCH SITES
   └─→ Site selector changed
      └─→ Streamlit reruns
         └─→ All cached data invalidated (key changed)
         └─→ New data loaded for new site
         └─→ Both tabs show new site's data
```

---

This architecture ensures:
- ✅ **Modularity**: Easy to add/modify tabs
- ✅ **Performance**: Caching avoids redundant computation
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Scalability**: Can handle more sites/gauges/analyses
- ✅ **Robustness**: Error handling throughout
