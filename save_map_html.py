"""
save_map_html.py - Export the Dash/Folium map as standalone HTML files
Creates embeddable HTML versions of the side-by-side maps
"""

import folium
from folium.plugins import MarkerCluster
from api311 import Year


def create_standalone_maps():
    """Create and save standalone HTML maps for 2015 and 2025"""
    print("Loading data...")
    year15 = Year("data/cleaned2015.csv")
    year25 = Year("data/cleaned2025.csv")
    year15.make_points()
    year25.make_points()

    print(f"Loaded 2015: {len(year15.data):,} records")
    print(f"Loaded 2025: {len(year25.data):,} records")

    # Sample data for performance (5000 points each)
    data15_sample = year15.data.sample(n=min(5000, len(year15.data)), random_state=42)
    data25_sample = year25.data.sample(n=min(5000, len(year25.data)), random_state=42)

    # Create 2015 map
    print("\nCreating 2015 map...")
    map_2015 = folium.Map(location=[42.3601, -71.0589], zoom_start=12)
    cluster_15 = MarkerCluster().add_to(map_2015)

    for _, row in data15_sample.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"<b>{row['case_title']}</b><br>{row['type']}<br>{row['location']}",
            tooltip=row['type']
        ).add_to(cluster_15)

    map_2015.save('figures/map_2015.html')
    print("Saved: figures/map_2015.html")

    # Create 2025 map
    print("Creating 2025 map...")
    map_2025 = folium.Map(location=[42.3601, -71.0589], zoom_start=12)
    cluster_25 = MarkerCluster().add_to(map_2025)

    for _, row in data25_sample.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"<b>{row['case_title']}</b><br>{row['type']}<br>{row['location']}",
            tooltip=row['type']
        ).add_to(cluster_25)

    map_2025.save('figures/map_2025.html')
    print("Saved: figures/map_2025.html")

    print("\nMaps created! You can now embed them in your website.")
    print("Note: Full interactive filtering still requires running map_app.py")


if __name__ == "__main__":
    create_standalone_maps()