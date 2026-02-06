import pandas as pd
import geopandas as gpd
import folium
from dash import Dash, html, dcc
import dash_leaflet as dl


class Year:
    def __init__(self, fp: str):
        self.data = pd.read_csv(fp)
        self.gpd = None
        self.start_box = (42.3601, -71.0589)
        self.cache = None  # store subsets in cache - full data stays intact in data

    def make_points(self) -> None:
        self.data["geometry"] = gpd.points_from_xy(
            self.data.longitude, self.data.latitude
        )
        self.data = gpd.GeoDataFrame(self.data, geometry="geometry", crs="EPSG:4326")
        self.data = self.data.dropna(subset=["geometry"])
        self.data = self.data[~self.data.geometry.is_empty]
        self.cache = self.data  # by default assign full data to cache

    def serve_cache(self) -> folium.Map:
        map = folium.Map(location=self.start_box, zoom_start=10)

        for _, row in self.cache.iterrows():
            folium.Marker(
                [row["geometry"].y, row["geometry"].x],
                popup=row[["case_title", "subject", "location"]],
            ).add_to(map)
        return map

    def get_neighborhood_subset(self):
        pass
