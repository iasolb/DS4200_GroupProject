from api311 import Year
import folium
import geopandas as gpd


def main():
    data15 = Year("data/311_2015.csv")
    data25 = Year("data/311_2025.csv")
    print("2015 311 Service Request Data:")
    print(data15.data.head())
    print("2025 311 Service Request Data:")
    print(data25.data.head())


if __name__ == "__main__":
    main()
