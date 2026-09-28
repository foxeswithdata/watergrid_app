# Quick Start: 5-Minute Setup

Get your modular app running in 5 minutes.

## Step 1: File Setup (1 minute)

Create this directory structure:
```
my_app/
├── main_app.py
├── tab1_watercycles.py
├── tab2_temperature.py
├── data_loader.py
├── utils.py
├── data/
│   ├── discharge_G1.csv
│   ├── discharge_G2.csv
│   ├── tmax_combined_G1.csv
│   └── tmax_combined_G2.csv
└── README.md
```

Copy all `.py` files from the outputs folder.

## Step 2: Install Dependencies (1 minute)

```bash
pip install streamlit pandas numpy plotly
```

## Step 3: Configure Sites (1 minute)

Edit `data_loader.py`, find `SITES_CONFIG`:

```python
SITES_CONFIG = {
    "Bioklimatic Park": {
        "gauges": ["G1", "G2"],  # Add your gauges
        "water_file": "discharge_{gauge}.csv",
        "temp_file": "tmax_combined_{gauge}.csv"
    }
}
```

Add or modify sites to match your CSV file names.

## Step 4: Add Data (1 minute)

Place your CSV files in the `data/` folder:
- `discharge_G1.csv` (water cycle data)
- `tmax_combined_G1.csv` (temperature data)

CSV format:
```
date,scenario1,scenario2,scenario3,...
01/01/1961,value1,value2,value3,...
...
```

## Step 5: Run! (1 minute)

```bash
streamlit run main_app.py
```

Open your browser to `http://localhost:8501`

---

## ✨ What You'll See

1. **Sidebar**: Site and gauge selection dropdowns
2. **Tab 1**: Water Cycles Analysis (placeholder - add your code)
3. **Tab 2**: Temperature Analysis (placeholder - add your code)

## 🛠️ Next: Add Your Visualizations

### Option A: Copy from Your Notebook

1. Open `tab2_temperature.py`
2. Find the section: `# if 'timeseries_figure' in data:`
3. Replace with your Plotly code

### Option B: Use the Migration Guide

Follow `MIGRATION_GUIDE.md` for step-by-step instructions.

## 🎯 Your First Customization

**Change the tab title:**

In `main_app.py`, find:
```python
tab1, tab2 = st.tabs([
    "💧 Water Cycles Analysis",
    "🌡️ Temperature Analysis"
])
```

Change to:
```python
tab1, tab2 = st.tabs([
    "💧 My Water Data",
    "🌡️ My Temperature Data"
])
```

Save and refresh the browser - it updates instantly!

## 📊 Testing with Dummy Data

If you don't have data yet, create dummy data to test the layout:

**data/discharge_G1.csv:**
```csv
date,SSP126_model1,SSP126_model2,SSP245_model1,SSP245_model2
01/01/1961,10.5,11.2,10.8,11.5
02/01/1961,10.3,11.0,10.6,11.3
03/01/1961,10.7,11.4,11.0,11.7
```

**data/tmax_combined_G1.csv:**
```csv
date,SSP126_model1,SSP126_model2,SSP245_model1,SSP245_model2
01/01/1961,15.2,14.8,15.5,15.1
02/01/1961,15.5,15.1,15.8,15.4
03/01/1961,15.8,15.4,16.1,15.7
```

## 🎓 What Each File Does

| File | Purpose |
|------|---------|
| `main_app.py` | Entry point - layout, tabs, sidebar |
| `tab1_watercycles.py` | Water cycle analysis display |
| `tab2_temperature.py` | Temperature analysis display |
| `data_loader.py` | Load and process data |
| `utils.py` | Shared functions |

## 🔗 Key Features You Get

✅ Persistent site/gauge selection across tabs  
✅ Built-in explanatory text  
✅ Data export to CSV  
✅ Modular architecture (easy to add tabs)  
✅ Per-tab sidebar controls  
✅ Responsive layout  

## 🚨 Troubleshooting

**App won't start?**
```bash
# Check you have streamlit installed
pip list | grep streamlit

# Clear cache
streamlit cache clear

# Try running again
streamlit run main_app.py
```

**Can't find data files?**
- Make sure `data/` folder exists
- Check filenames match exactly (case-sensitive)
- Verify CSV column headers

**Dropdown shows no options?**
- Check `SITES_CONFIG` in `data_loader.py`
- Make sure data files exist for each gauge

**Visualization doesn't show?**
- The placeholder code currently shows "Not available"
- You need to add your actual Plotly code (see Migration Guide)

## 📈 Next Steps

1. ✅ **Get app running** with dummy data
2. 🔧 **Add your real data** to `data/` folder
3. 📊 **Migrate visualization code** from your notebook
4. 🎨 **Customize styling** and explanatory text
5. 🚀 **Deploy** (optional)

## 💡 Tips

- **Develop incrementally**: Start with one visualization, then add more
- **Use browser refresh**: Changes to `.py` files auto-reload
- **Check the sidebar**: Lots of useful info and settings there
- **Read the migration guide**: When you're ready to add your code

## 🎉 You're Done!

You now have a production-ready, modular Streamlit app that:
- Manages multiple sites and gauges
- Displays multiple analyses in separate tabs
- Maintains clean, readable code
- Is easy to extend and maintain

**Happy analyzing! 📊**

---

## 📞 Quick Reference

```bash
# Run the app
streamlit run main_app.py

# Clear cache if things seem stale
streamlit cache clear

# Open browser automatically (Streamlit does this)
# Or go to http://localhost:8501

# Stop the app
# Press Ctrl+C in terminal
```

## 📚 Useful Links

- Streamlit Docs: https://docs.streamlit.io
- Plotly Examples: https://plotly.com/python/
- Pandas Guide: https://pandas.pydata.org/docs/
- This Repository: Check README.md for full documentation
