
# Install required libraries before running:
# pip install pandas geopandas shapely duckdb
 
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree
import duckdb
import os

# Connect to DuckDB and load spatial extension
con = duckdb.connect(database=':memory:')
con.execute("INSTALL spatial;")
con.execute("LOAD spatial;")

# Run query to extract San Jose buildings to GeoJSON
con.execute("""
COPY (
    SELECT
        id,
        level,
        height,
        names.primary AS primary_name,
        sources[1].dataset AS primary_source,
        geometry
    FROM read_parquet(
        's3://overturemaps-us-west-2/release/2025-05-21.0/theme=buildings/type=*/*',
        hive_partitioning=1
    )
    WHERE bbox.xmin > -122.10 AND bbox.xmax < -121.60
      AND bbox.ymin > 37.10 AND bbox.ymax < 37.45
) TO 'sanjose_buildings.geojson' (FORMAT GDAL, DRIVER 'GeoJSON');
""")

# Run query to extract San Jose POIs to GeoJSON
con.execute("""
COPY(
    SELECT
        id,
        names.primary AS name,
        CAST(addresses AS JSON) AS addresses,
        confidence,
        geometry
    FROM read_parquet(
        's3://overturemaps-us-west-2/release/2025-04-23.0/theme=places/type=place/*',
        filename=true,
        hive_partitioning=1
    )
    WHERE bbox.xmin BETWEEN -122.10 AND -121.60
      AND bbox.ymin BETWEEN 37.10 AND 37.45
) TO 'sanjose_pois.geojson' (FORMAT GDAL, DRIVER 'GeoJSON');
""")

# Load and project to meters
pois = gpd.read_file("sanjose_pois.geojson").to_crs(epsg=32610)
buildings = gpd.read_file("sanjose_buildings.geojson").to_crs(epsg=32610)

# Determine POIs within buildings
within = gpd.sjoin(pois, buildings, how="left", predicate="within").reset_index()
poi_inside_flags = within.groupby("index")["index_right"].apply(lambda x: x.notna().any())
pois["inside_building"] = pois.index.to_series().map(poi_inside_flags).fillna(False)

# POIs not inside any building
outside_pois = pois[~pois["inside_building"]].copy()
buffered = outside_pois.copy()
buffered["geometry"] = buffered.geometry.buffer(50)
candidates = gpd.sjoin(buildings, buffered, how="inner", predicate="intersects")

# Group candidate buildings
grouped = candidates.groupby("index_right").agg({
    "id_left": list,
    "primary_name": list,
    "height": list
}).reset_index()

# Build lookup dictionaries
name_to_buildings = {}
for idx, row in buildings.iterrows():
    name = str(row["primary_name"]).strip().lower()
    if name:
        name_to_buildings.setdefault(name, []).append(row)

building_centroids = buildings.geometry.centroid
str_tree = STRtree(building_centroids)
centroid_to_building = dict(zip(building_centroids, buildings.index))

def find_best_building_optimized(poi_row):
    poi_geom = poi_row.geometry
    poi_name = str(poi_row["name"]).strip().lower()

    if poi_name in name_to_buildings:
        matches = gpd.GeoDataFrame(name_to_buildings[poi_name])
        matches["dist"] = matches.geometry.centroid.distance(poi_geom)
        return matches.sort_values("dist").iloc[0].geometry.centroid

    match_candidates = candidates[candidates.index_right == poi_row.name]
    if not match_candidates.empty:
        match_candidates = match_candidates.copy()
        match_candidates["dist"] = match_candidates.geometry.centroid.distance(poi_geom)
        return match_candidates.sort_values("dist").iloc[0].geometry.centroid

    nearby_centroids = str_tree.query(poi_geom.buffer(200))
    valid_centroids = [c for c in nearby_centroids if isinstance(c, BaseGeometry)]

    if valid_centroids:
        nearest = min(valid_centroids, key=lambda c: poi_geom.distance(c))
        best_building = buildings.loc[centroid_to_building[nearest]]
        return best_building.geometry.centroid

    return poi_geom

# Snap POIs
outside_pois["new_geometry"] = outside_pois.apply(find_best_building_optimized, axis=1)
inside_pois = pois[pois["inside_building"]].copy()
inside_pois["new_geometry"] = inside_pois.geometry

# Combine and save
final = pd.concat([inside_pois, outside_pois], ignore_index=True)
final = final.set_geometry("new_geometry").set_crs(epsg=32610).to_crs(epsg=4326)
final = final.drop(columns=["geometry", "inside_building"]).rename(columns={"new_geometry": "geometry"})
final = final.set_geometry("geometry")
final.to_file("snapped_only_outside_pois.geojson", driver="GeoJSON")

# Optional: save to Google Drive (uncomment if running in Colab)
# from google.colab import drive
# drive.mount('/content/drive')
# output_path = "/content/drive/MyDrive/snapped_only_outside_pois.geojson"
# final.to_file(output_path, driver="GeoJSON")
