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
        horizontal_spacing=0.12
    )

    # 2015 heatmap
    fig.add_trace(
        go.Heatmap(
            z=monthly_15_filtered.values,
            x=monthly_15_filtered.columns,
            y=monthly_15_filtered.index,
            colorscale='YlOrRd',
            showscale=True,
            hovertemplate='<b>%{y}</b><br>%{x}<br>Requests: %{z:.0f}<extra></extra>',
            colorbar=dict(title="Requests", x=0.46, len=0.8)
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
            hovertemplate='<b>%{y}</b><br>%{x}<br>Requests: %{z:.0f}<extra></extra>',
            colorbar=dict(title="Requests", x=1.0, len=0.8)
        ),
        row=1, col=2
    )

    fig.update_layout(
        title={
            'text': "Seasonal Patterns in Boston 311 Requests",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        height=600,
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=180, r=100, t=100, b=80)
    )

    # Update x-axes
    fig.update_xaxes(
        title_text="Month",
        tickangle=45,
        tickfont=dict(size=11),
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="Month",
        tickangle=45,
        tickfont=dict(size=11),
        row=1, col=2
    )

    # Update y-axes with better spacing
    fig.update_yaxes(
        title_text="Request Type",
        tickfont=dict(size=10),
        automargin=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Request Type",
        tickfont=dict(size=10),
        automargin=True,
        row=1, col=2
    )

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

    fig = go.Figure()

    # Add bars with color scale
    fig.add_trace(go.Bar(
        x=list(range(len(drift))),
        y=drift["distance"],
        marker=dict(
            color=drift["distance"],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Drift", len=0.7),
            line=dict(color='black', width=0.5)
        ),
        hovertemplate='<b>%{customdata}</b><br>' +
                      'Drift: %{y:.3f}<br>' +
                      'Rank: %{x}<br>' +
                      '<extra></extra>',
        customdata=drift["area"],
        name=''
    ))

    # Add median line
    median = drift["distance"].median()
    fig.add_hline(
        y=median,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=f"Median: {median:.3f}",
        annotation_position="top right",
        annotation_font=dict(size=12, color="red")
    )

    fig.update_layout(
        title={
            'text': "311 Signature Drift by Neighborhood",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        xaxis_title="Neighborhoods (ranked by drift)",
        yaxis_title="Cosine Distance (2015 → 2025)",
        height=650,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(drift))),
            ticktext=drift["area"],
            tickangle=60,
            tickfont=dict(size=10),
            automargin=True
        ),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        plot_bgcolor='white',
        margin=dict(b=150, t=80, l=80, r=80)
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


def create_composition_bars_plotly(year15, year25):
    """Interactive composition bars with color legend"""
    print("Creating interactive composition bars...")

    # Clean data
    data15 = year15.data[
        year15.data["neighborhood"].notna() &
        (year15.data["neighborhood"].str.strip() != "")
    ].copy()

    data25 = year25.data[
        year25.data["neighborhood"].notna() &
        (year25.data["neighborhood"].str.strip() != "")
    ].copy()

    # Get top 6 neighborhoods
    top_neighborhoods = data15["neighborhood"].value_counts().head(6).index.tolist()

    # Build data for all neighborhoods
    data_list = []

    for hood in top_neighborhoods:
        hood_15 = data15[data15["neighborhood"] == hood]
        hood_25 = data25[data25["neighborhood"] == hood]

        # Get top 5 combined types for this neighborhood
        combined = pd.concat([hood_15["type"], hood_25["type"]])
        top_types = combined.value_counts().head(5).index.tolist()

        for req_type in top_types:
            count_15 = (hood_15["type"] == req_type).sum()
            count_25 = (hood_25["type"] == req_type).sum()

            if count_15 > 0:
                data_list.append({
                    "Neighborhood": hood,
                    "Request Type": clean_request_type_name(req_type),
                    "Count": count_15,
                    "Year": "2015"
                })

            if count_25 > 0:
                data_list.append({
                    "Neighborhood": hood,
                    "Request Type": clean_request_type_name(req_type),
                    "Count": count_25,
                    "Year": "2025"
                })

    df = pd.DataFrame(data_list)

    # Create subplots for each neighborhood
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=top_neighborhoods,
        horizontal_spacing=0.12,
        vertical_spacing=0.15
    )

    colors = {'2015': '#4C72B0', '2025': '#DD8452'}

    for idx, hood in enumerate(top_neighborhoods):
        row = idx // 3 + 1
        col = idx % 3 + 1

        hood_df = df[df["Neighborhood"] == hood]

        # Add 2015 bars
        data_2015 = hood_df[hood_df["Year"] == "2015"]
        fig.add_trace(
            go.Bar(
                y=data_2015["Request Type"],
                x=data_2015["Count"],
                name='2015',
                marker_color=colors['2015'],
                orientation='h',
                showlegend=(idx == 0),  # Only show legend once
                hovertemplate='<b>%{y}</b><br>2015: %{x} requests<extra></extra>'
            ),
            row=row, col=col
        )

        # Add 2025 bars
        data_2025 = hood_df[hood_df["Year"] == "2025"]
        fig.add_trace(
            go.Bar(
                y=data_2025["Request Type"],
                x=data_2025["Count"],
                name='2025',
                marker_color=colors['2025'],
                orientation='h',
                showlegend=(idx == 0),
                hovertemplate='<b>%{y}</b><br>2025: %{x} requests<extra></extra>'
            ),
            row=row, col=col
        )

    fig.update_layout(
        title={
            'text': "How Neighborhood Request Patterns Changed: 2015 vs 2025",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        height=800,
        font=dict(family="Arial, sans-serif", size=11),
        barmode='group',
        legend=dict(
            title=dict(text="Year", font=dict(size=13)),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(l=150, r=50, t=120, b=60)
    )

    # Update all x-axes
    for i in range(1, 7):
        row = (i - 1) // 3 + 1
        col = (i - 1) % 3 + 1
        fig.update_xaxes(title_text="Requests", row=row, col=col)

    fig.write_html('figures/composition_bars.html')
    print("Saved: figures/composition_bars.html")

    return fig


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
    create_composition_bars_plotly(year15, year25)  # Added!

    print("\nAll interactive visualizations saved to figures/!")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()