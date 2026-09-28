"""
Tab 1: Water Cycles Analysis
=============================
Displays water cycle outputs with explanatory text.
This is where your original watercycles_all.py logic goes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_loader import load_watercycles_data

CATEGORY_COLORS = {
    "white": "white",
    "positive": "lightsteelblue",   # Inputs
    "negative": "chocolate",        # Outputs
    "storage": "#00CC96",           # Storage (parent)
    "storpos": "#33AC86",           # Storage pos.
    "storneg": "#539C66",           # Storage neg.
}

# ---------------------------------------------------------------------------
# Charting
# ---------------------------------------------------------------------------

def _nudge_for_plotly(labels, parents, values, epsilon=1e-6, passes=5):
    """Plotly's Sunburst with branchvalues='total' silently renders BLANK
    (no error) if a parent's value is even negligibly less than the sum of
    its children — which floating-point rounding can trigger even when the
    underlying data is perfectly balanced (parent == sum(children) exactly,
    with zero slack). Balanced water-budget data hits this a lot.

    This nudges the largest child in each sibling group down by a tiny
    epsilon wherever needed, guaranteeing parent >= sum(children). Several
    passes handle multi-level trees where a nudge at one level could
    affect the level below it.
    """
    values = list(values)
    label_to_idx = {label: i for i, label in enumerate(labels)}

    children_by_parent = {}
    for i, p in enumerate(parents):
        if p:  # skip the root, which has an empty-string parent
            children_by_parent.setdefault(p, []).append(i)

    for _ in range(passes):
        changed = False
        for parent_label, child_idxs in children_by_parent.items():
            if parent_label not in label_to_idx:
                continue
            parent_idx = label_to_idx[parent_label]
            parent_value = values[parent_idx]
            children_sum = sum(values[i] for i in child_idxs)

            if children_sum >= parent_value:
                biggest_idx = max(child_idxs, key=lambda i: values[i])
                excess = children_sum - parent_value
                values[biggest_idx] -= (excess + epsilon)
                changed = True
        if not changed:
            break

    return values


def build_sunburst(labels, parents, colors, values, year_label, site_name):
    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Value: %{value:.1f} mm<br>"
                "Share of parent: %{percentParent:.1%}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title_text=f"CWatM Water Balance — {site_name} ({year_label})",
        template="presentation",
        height=700,
        margin=dict(t=60, l=10, r=10, b=10),
    )
    return fig


def render_tab1(site: str, gauge: str):
    """
    Render the Water Cycles Analysis tab.
    
    Args:
        site: Selected site name
        gauge: Selected gauge/location name
    """
    
    # ========================================
    # INTRODUCTION & EXPLANATION
    # ========================================
    st.markdown("## Water Cycles Overview")
    
    with st.expander("📖 **How to interpret this tab**", expanded=False):
        st.markdown("""
        ### What are water cycles?
        This tab presents an analysis of water cycle to explore water input/outputs
        across a basin.
        
        Each ring segment represents a component of the water balance
        (inputs, outputs, and storage changes), scaled in mm over the
        basin. Click a segment to zoom into that branch; click the
        centre to zoom back out.
        """)
    
    # ========================================
    # LOAD DATA
    # ========================================
    
    try:
        labels, parents, colors, values_out = load_watercycles_data(site, gauge)
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Make sure the data files are available in the data directory.")
        return

    year = st.selectbox("Select Year for Water Balance", sorted(values_out.keys()), index=len(values_out)-1)

    plot_values = _nudge_for_plotly(labels, parents, values_out[year])
    fig = build_sunburst(labels, parents, colors, plot_values, year, site)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

