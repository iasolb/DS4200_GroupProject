"""
plotly_visualizations.py - Create interactive HTML visualizations with hover tooltips
Converts matplotlib static visualizations to interactive Plotly versions
"""

from signatures import SignatureAnalyzer
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from api311 import Year, clean_request_type_name


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

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('2015', '2025'),
        horizontal_spacing=0.12
    )

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

    fig.update_xaxes(title_text="Month", tickangle=45, tickfont=dict(size=11), row=1, col=1)
    fig.update_xaxes(title_text="Month", tickangle=45, tickfont=dict(size=11), row=1, col=2)
    fig.update_yaxes(title_text="Request Type", tickfont=dict(size=10), automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="Request Type", tickfont=dict(size=10), automargin=True, row=1, col=2)

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

    drift = drift[drift["area"].notna() & (drift["area"].str.strip() != "")]

    counts_15 = year15.data["neighborhood"].value_counts()
    counts_25 = year25.data["neighborhood"].value_counts()
    drift["avg_requests"] = drift["area"].map(
        lambda x: (counts_15.get(x, 0) + counts_25.get(x, 0)) / 2
    )

    fig = go.Figure()

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
    """Cluster comparison as facet bar charts showing request type profiles per cluster"""
    print("Creating interactive cluster comparison...")

    sa = SignatureAnalyzer(area_col="neighborhood", type_col="type")

    sigs_15 = sa.build_signatures(year15.data, min_requests=30)
    sigs_25 = sa.build_signatures(year25.data, min_requests=30)

    kmeans_15 = KMeans(n_clusters=4, random_state=42, n_init=10).fit(sigs_15)
    kmeans_25 = KMeans(n_clusters=4, random_state=42, n_init=10).fit(sigs_25)

    labels_15 = pd.Series(kmeans_15.labels_, index=sigs_15.index)
    labels_25 = pd.Series(kmeans_25.labels_, index=sigs_25.index)

    cluster_colors = ['#e8a090', '#f4a460', '#9eb8d9', '#d4a0c0']

    def build_cluster_profiles(sigs, labels):
        """For each cluster, get top 7 request types by mean relative frequency"""
        profiles = {}
        for i in range(4):
            member_sigs = sigs[labels == i]
            mean_freq = member_sigs.mean()
            top7 = mean_freq.nlargest(7)
            top7.index = [clean_request_type_name(t) for t in top7.index]
            # Truncate long names
            top7.index = [t[:22] + '...' if len(t) > 22 else t for t in top7.index]
            hoods = sorted(labels[labels == i].index.tolist())
            profiles[i] = {"freqs": top7, "neighborhoods": hoods}
        return profiles

    def make_cluster_fig(profiles, year_label):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                f"Cluster {i} — {len(profiles[i]['neighborhoods'])} neighborhoods"
                for i in range(4)
            ],
            horizontal_spacing=0.18,
            vertical_spacing=0.25
        )

        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

        for i, (row, col) in enumerate(positions):
            freqs = profiles[i]["freqs"]
            hoods = profiles[i]["neighborhoods"]
            hood_str = "<br>".join(hoods)

            fig.add_trace(
                go.Bar(
                    x=freqs.index.tolist(),
                    y=freqs.values,
                    marker_color=cluster_colors[i],
                    marker_line=dict(color='white', width=0.5),
                    hovertemplate=(
                        '<b>%{x}</b><br>'
                        'Relative Frequency: %{y:.1%}<br><br>'
                        f'<b>Neighborhoods:</b><br>{hood_str}'
                        '<extra></extra>'
                    ),
                    showlegend=False
                ),
                row=row, col=col
            )

            fig.update_xaxes(
                tickangle=35,
                tickfont=dict(size=8),
                automargin=True,
                row=row, col=col
            )
            fig.update_yaxes(
                title_text="Relative Frequency",
                tickformat='.0%',
                tickfont=dict(size=9),
                row=row, col=col
            )

        fig.update_layout(
            title={
                'text': f"{year_label} Neighborhood Cluster Profiles",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            height=1000,
            font=dict(family="Arial, sans-serif", size=10),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=40, t=100, b=160),
            annotations=[
                dict(
                    text="Hover over each bar to see the top request types and neighborhoods in that cluster.",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.13,
                    xanchor="center",
                    font=dict(size=11, color="gray")
                )
            ]
        )

        return fig

    profiles_15 = build_cluster_profiles(sigs_15, labels_15)
    profiles_25 = build_cluster_profiles(sigs_25, labels_25)

    fig_15 = make_cluster_fig(profiles_15, "2015")
    fig_25 = make_cluster_fig(profiles_25, "2025")

    fig_15.write_html('figures/cluster_profiles_2015.html')
    fig_25.write_html('figures/cluster_profiles_2025.html')
    print("Saved: figures/cluster_profiles_2015.html")
    print("Saved: figures/cluster_profiles_2025.html")

    return fig_15, fig_25, labels_15, labels_25


def create_composition_bars_plotly(year15, year25):
    """Interactive composition bars with color legend"""
    print("Creating interactive composition bars...")

    data15 = year15.data[
        year15.data["neighborhood"].notna() &
        (year15.data["neighborhood"].str.strip() != "")
    ].copy()

    data25 = year25.data[
        year25.data["neighborhood"].notna() &
        (year25.data["neighborhood"].str.strip() != "")
    ].copy()

    top_neighborhoods = data15["neighborhood"].value_counts().head(6).index.tolist()

    data_list = []

    for hood in top_neighborhoods:
        hood_15 = data15[data15["neighborhood"] == hood]
        hood_25 = data25[data25["neighborhood"] == hood]

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

    # 2 columns, 3 rows — gives each chart more horizontal room
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=top_neighborhoods,
        horizontal_spacing=0.22,
        vertical_spacing=0.10
    )

    colors = {'2015': '#4C72B0', '2025': '#DD8452'}

    for idx, hood in enumerate(top_neighborhoods):
        row = idx // 2 + 1
        col = idx % 2 + 1

        hood_df = df[df["Neighborhood"] == hood]

        data_2015 = hood_df[hood_df["Year"] == "2015"]
        fig.add_trace(
            go.Bar(
                y=data_2015["Request Type"],
                x=data_2015["Count"],
                name='2015',
                marker_color=colors['2015'],
                orientation='h',
                showlegend=(idx == 0),
                hovertemplate='<b>%{y}</b><br>2015: %{x} requests<extra></extra>'
            ),
            row=row, col=col
        )

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
        height=1400,
        font=dict(family="Arial, sans-serif", size=11),
        barmode='group',
        legend=dict(
            title=dict(text="Year", font=dict(size=13)),
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(l=220, r=60, t=120, b=60)
    )

    for i in range(1, 7):
        row = (i - 1) // 2 + 1
        col = (i - 1) % 2 + 1
        fig.update_xaxes(title_text="Requests", tickfont=dict(size=10), row=row, col=col)
        fig.update_yaxes(tickfont=dict(size=10), automargin=True, row=row, col=col)

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

    create_monthly_heatmap_plotly(year15, year25)
    create_signature_drift_plotly(year15, year25)
    create_cluster_comparison_plotly(year15, year25)
    create_composition_bars_plotly(year15, year25)

    print("\nAll interactive visualizations saved to figures/!")


if __name__ == "__main__":
    main()