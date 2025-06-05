# import json 
# with open ('places.geojson', 'r') as f:
#     # print(f.read())
#     data = json.load(f)
#     properties = data['features']
#     for i in properties:
#         geo = i['geometry']['coordinates']
#         m = geo[0]+2
#         n = geo[1]+2
#         print([m,n])

# import json 
# import geopandas as gpd
# gdf = gpd.read_file("test.geojson")
# gdf = gdf.to_crs("EPSG:3310")
# # print(gdf['geometry'])
# # print(type(gdf['geometry']))
# with open ('test.geojson', 'r') as f:
#     # print(f.read())
#     data = json.load(f)
#     properties = data['features']
#     dist = []
#     for i in range(0, len(gdf)-1):
#         distance_meters = gdf.geometry.iloc[i].distance(gdf.geometry.iloc[i + 1])
#         # print(distance_meters)
#         dist.append(distance_meters)
#         # geo = i['geometry']['coordinates']
#         # m = geo[0]-10
#         # n = geo[1]-10
#     # print(len(dist))
#     # print(len(properties))
#     for i in range(0, len(properties)-1):
#         geo = properties[i]['geometry']['coordinates']
#         m = geo[0]-dist[i]
#         n = geo[1]-dist[i]
#         properties[i]['geometry']['coordinates'] = [m,n]

# with open('hi.geojson', 'w') as f:
#     json.dump(data, f, indent=2)
#         # print(i['geometry']['coordinates'])

# import geopandas as gpd
# from shapely.affinity import translate
# import json

# # Load and project GeoJSON to a meter-based CRS (e.g., California Albers)
# gdf = gpd.read_file("test.geojson")
# gdf = gdf.to_crs("EPSG:3310")
# # print(gdf.iloc[0]['name'])

# # Offset each point by the distance to the next point
# # all_dist = []
# for i in range(len(gdf) - 1):
#     # dist = gdf.geometry.iloc[i].distance(gdf.geometry.iloc[i + 1])
#     for j in range(len(gdf)-1):
#         if i == j:
#             continue 
#         dist = gdf.geometry.iloc[i].distance(gdf.geometry.iloc[j])
#         # all_dist.append(dist)
#         if dist < 20:
#             gdf.loc[gdf.index[i], 'geometry'] = translate(gdf.geometry.iloc[i], xoff=dist, yoff=dist)
    
#     # Use .loc with the index to avoid chained assignment
#     # gdf.loc[gdf.index[i], 'geometry'] = translate(gdf.geometry.iloc[i], xoff=dist, yoff=0)

# # Optional: Convert back to WGS84 for saving to GeoJSON
# gdf = gdf.to_crs("EPSG:4326")

# # Save to new GeoJSON
# gdf.to_file("hi.geojson", driver="GeoJSON")


# import geopandas as gpd
# from shapely.affinity import translate
# import numpy as np

# # Load and project GeoJSON to a meter-based CRS
# gdf = gpd.read_file("test.geojson")
# gdf = gdf.to_crs("EPSG:3310")

# # Parameters
# min_dist = 20  # minimum allowed distance between points
# nudge_step = 5  # how far to move overlapping points

# # Track adjusted geometries
# new_geometries = gdf.geometry.copy()

# # Only check each pair once
# for i in range(len(gdf)):
#     for j in range(i + 1, len(gdf)):
#         geom_i = new_geometries.iloc[i]
#         geom_j = new_geometries.iloc[j]
#         dist = geom_i.distance(geom_j)

#         if dist < 20:
#             # Calculate vector from i to j
#             dx = geom_j.x - geom_i.x
#             dy = geom_j.y - geom_i.y
#             norm = np.hypot(dx, dy) if dx != 0 or dy != 0 else 1

#             # Nudge point j slightly away from i
#             offset_x = (dx / norm) * nudge_step
#             offset_y = (dy / norm) * nudge_step
#             new_geom_j = translate(geom_j, xoff=offset_x, yoff=offset_y)

#             # Update geometry
#             new_geometries.iloc[j] = new_geom_j

# # Assign new geometries
# gdf['geometry'] = new_geometries

# # Reproject back to WGS84 and save
# gdf = gdf.to_crs("EPSG:4326")
# gdf.to_file("hi.geojson", driver="GeoJSON")

# import geopandas as gpd
# from shapely.affinity import translate
# import numpy as np

# # Load and project GeoJSON to a meter-based CRS
# gdf = gpd.read_file("test.geojson")
# gdf = gdf.to_crs("EPSG:3310")

# # Parameters
# min_dist = 20  # desired minimum distance between points

# # Use a copy to store adjusted geometries
# new_geometries = gdf.geometry.copy()

# # Process unique pairs
# for i in range(len(gdf)):
#     for j in range(i + 1, len(gdf)):
#         geom_i = new_geometries.iloc[i]
#         geom_j = new_geometries.iloc[j]

#         dx = geom_j.x - geom_i.x
#         dy = geom_j.y - geom_i.y
#         dist = np.hypot(dx, dy)

#         if dist < min_dist and dist != 0:
#             # Amount to move each point to resolve overlap
#             overlap = (min_dist - dist) / 2
#             ux = dx / dist
#             uy = dy / dist

#             # Move point i backwards
#             new_geom_i = translate(geom_i, xoff=-ux * overlap, yoff=-uy * overlap)
#             # Move point j forwards
#             new_geom_j = translate(geom_j, xoff=ux * overlap, yoff=uy * overlap)

#             # Update both geometries
#             new_geometries.iloc[i] = new_geom_i
#             new_geometries.iloc[j] = new_geom_j

# # Update original GeoDataFrame
# gdf['geometry'] = new_geometries

# # Convert back to WGS84
# gdf = gdf.to_crs("EPSG:4326")

# # Save to file
# gdf.to_file("hi.geojson", driver="GeoJSON")