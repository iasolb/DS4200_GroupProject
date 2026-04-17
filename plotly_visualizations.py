"""
plotly_visualizations.py - Create interactive HTML visualizations with hover tooltips
Converts matplotlib static visualizations to interactive Plotly versions
"""

from api311 import Year
from signatures import SignatureAnalyzer
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def clean_request_type_name(name):
    """Make request type names more readable"""
    replacements = {
        'Missed Trash/Recycling/Yard Waste/Bulk Item': 'Missed Trash/Recycling',
        'Request for Snow Plowing': 'Snow Plowing',
        'Request for Pothole Repair': 'Pothole Repair',
        'Street Light Outages': 'Street Lights',
        'Pothole Repair (Internal)': 'Pothole (Internal)',
        'Poor Conditions of Property': 'Poor Property Conditions',
        'Improper Storage of Trash (Barrels)': 'Improper Trash Storage',
        'Parks Lighting/Electrical Issues': 'Parks Lighting',
    }
    return replacements.get(name, name)


def create_monthly_heatmap_plotly(year15, year25):
    """Interactive monthly heatmap with hover details"""
    print("Creating interactive monthly heatmap...")

    summary_15 = year15.summarize("neighborhood", "type")
    summary_25 = year25.summarize("neighborhood", "type")

    monthly_15 = summary_15["monthly"]
    monthly_25 = summary_25["monthly"]

    top_types = year15.data["type"].value_counts().head(10).index.tolist()

    monthly_15_filtered = monthly_15.reindex(top_types).fillna(0)
    monthly_25_filtered = monthly_25.reindex(top_types).fillna(0)

    # Clean labels
    monthly_15_filtered.index = [clean_request_type_name(x) for x in monthly_15_filtered.index]
    monthly_25_filtered.index = [clean_request_type_name(x) for x in monthly_25_filtered.index]

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('2015', '2025'),
        horizontal_spacing=0.15
    )

    # 2015 heatmap
    fig.add_trace(
        go.Heatmap(
            z=monthly_15_filtered.values,
            x=monthly_15_filtered.columns,
            y=monthly_15_filtered.index,
            colorscale='YlOrRd',
            showscale=True,
            hovertemplate='<b>%{y}</b><br>%{x}<br>Requests: %{z}<extra></extra>',
            colorbar=dict(title="Requests", x=0.45)
        ),
        row=1, col=1
    )

    # 2025 heatmap
    fig.add_trace(
        go.Heatmap(
            z=monthly_25_filtered.values,
            x=monthly_25_filtered.columns,
            y=monthly_25_filtered.index,
            colorscale='YlOrRd',
            showscale=True,
            hovertemplate='<b>%{y}</b><br>%{x}<br>Requests: %{z}<extra></extra>',
            colorbar=dict(title="Requests", x=1.02)
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Seasonal Patterns in Boston 311 Requests",
        title_font_size=18,
        height=500,
        font=dict(family="Arial, sans-serif", size=12)
    )

    fig.update_xaxes(title_text="Month", tickangle=45, row=1, col=1)
    fig.update_xaxes(title_text="Month", tickangle=45, row=1, col=2)
    fig.update_yaxes(title_text="Request Type", row=1, col=1)
    fig.update_yaxes(title_text="Request Type", row=1, col=2)

    fig.write_html('figures/monthly_heatmap.html')
    print("Saved: figures/monthly_heatmap.html")

    return fig


def create_signature_drift_plotly(year15, year25):
    """Interactive signature drift with hover details"""
    print("Creating interactive signature drift...")

    sa = SignatureAnalyzer(area_col="neighborhood", type_col="type")

    sigs_15 = sa.build_signatures(year15.data, min_requests=30)
    sigs_25 = sa.build_signatures(year25.data, min_requests=30)

    drift = sa.compare_signatures(sigs_15, sigs_25)
    drift = drift.sort_values("distance", ascending=False).reset_index(drop=True)

    # Remove empty neighborhoods
    drift = drift[drift["area"].notna() & (drift["area"].str.strip() != "")]

    counts_15 = year15.data["neighborhood"].value_counts()
    counts_25 = year25.data["neighborhood"].value_counts()
    drift["avg_requests"] = drift["area"].map(
        lambda x: (counts_15.get(x, 0) + counts_25.get(x, 0)) / 2
    )

    # Create color scale
    colors = drift["distance"].values

    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=drift.index,
        y=drift["distance"],
        marker=dict(
            color=colors,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Drift")
        ),
        text=drift["area"],
        textposition='outside',
        textangle=-60,
        hovertemplate='<b>%{text}</b><br>' +
                      'Drift: %{y:.3f}<br>' +
                      '<extra></extra>',
        name=''
    ))

    # Add median line
    median = drift["distance"].median()
    fig.add_hline(
        y=median,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Median: {median:.3f}",
        annotation_position="top right"
    )

    fig.update_layout(
        title="311 Signature Drift by Neighborhood",
        title_font_size=18,
        xaxis_title="Neighborhoods (ranked by drift)",
        yaxis_title="Cosine Distance (2015 → 2025)",
        height=600,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=11),
        xaxis=dict(showticklabels=False)
    )

    fig.write_html('figures/signature_drift.html')
    print("Saved: figures/signature_drift.html")

    return fig


def create_cluster_comparison_plotly(year15, year25):
    """Interactive cluster comparison with hover details"""
    print("Creating interactive cluster comparison...")

    sa = SignatureAnalyzer(area_col="neighborhood", type_col="type")

    sigs_15 = sa.build_signatures(year15.data, min_requests=30)
    sigs_25 = sa.build_signatures(year25.data, min_requests=30)

    labels_15, _ = sa.cluster(sigs_15, k=4)
    labels_25, _ = sa.cluster(sigs_25, k=4)

    cluster_counts_15 = labels_15.value_counts().sort_index()
    cluster_counts_25 = labels_25.value_counts().sort_index()

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('2015 Neighborhood Clusters', '2025 Neighborhood Clusters')
    )

    cluster_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

    # 2015 bars
    fig.add_trace(
        go.Bar(
            x=[f'Cluster {i}' for i in range(4)],
            y=cluster_counts_15.values,
            marker_color=cluster_colors,
            hovertemplate='<b>%{x}</b><br>Neighborhoods: %{y}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )

    # 2025 bars
    fig.add_trace(
        go.Bar(
            x=[f'Cluster {i}' for i in range(4)],
            y=cluster_counts_25.values,
            marker_color=cluster_colors,
            hovertemplate='<b>%{x}</b><br>Neighborhoods: %{y}<extra></extra>',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="How Neighborhoods Group Together by Request Patterns",
        title_font_size=18,
        height=500,
        font=dict(family="Arial, sans-serif", size=12)
    )

    fig.update_xaxes(title_text="Cluster Group", row=1, col=1)
    fig.update_xaxes(title_text="Cluster Group", row=1, col=2)
    fig.update_yaxes(title_text="Number of Neighborhoods", row=1, col=1)
    fig.update_yaxes(title_text="Number of Neighborhoods", row=1, col=2)

    fig.write_html('figures/cluster_comparison.html')
    print("Saved: figures/cluster_comparison.html")

    return fig, labels_15, labels_25


def main():
    """Generate all interactive HTML visualizations"""
    print("Loading data...")
    year15 = Year("data/cleaned2015.csv")
    year25 = Year("data/cleaned2025.csv")

    print(f"Loaded 2015: {len(year15.data):,} records")
    print(f"Loaded 2025: {len(year25.data):,} records")

    import os
    os.makedirs('figures', exist_ok=True)

    # Generate interactive visualizations
    create_monthly_heatmap_plotly(year15, year25)
    create_signature_drift_plotly(year15, year25)
    create_cluster_comparison_plotly(year15, year25)

    print("\nAll interactive visualizations saved to figures/!")


if __name__ == "__main__":
    main()