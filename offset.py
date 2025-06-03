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

import geopandas as gpd
from shapely.affinity import translate
from shapely.geometry import Point
import numpy as np
from scipy.spatial import cKDTree

# Load and project GeoJSON to a meter-based CRS
gdf = gpd.read_file("test.geojson")
gdf = gdf.to_crs("EPSG:3310")

# Parameters
min_dist = 20  # desired minimum distance between points
max_iterations = 50
tolerance = 0.1

def separate_points_optimized(geometries, min_distance, max_iter=50, tol=0.1):
    """
    Optimized point separation using KDTree for spatial queries and vectorized operations
    """
    n = len(geometries)
    
    # Extract coordinates as numpy arrays for vectorized operations
    coords = np.array([[geom.x, geom.y] for geom in geometries])
    
    for iteration in range(max_iter):
        # Build KDTree for efficient neighbor queries
        tree = cKDTree(coords)

        # This class provides an index into a set of k-dimensional points 
        # which can be used to rapidly look up the nearest neighbors of any point.
        
        # Find all pairs within min_distance
        pairs = tree.query_pairs(r=min_distance, output_type='ndarray')
        
        if len(pairs) == 0:
            print(f"No overlaps found after {iteration + 1} iterations")
            break
        
        print(f"Iteration {iteration + 1}: found {len(pairs)} overlapping pairs")
        
        # Vectorized distance and movement calculations
        i_coords = coords[pairs[:, 0]]
        j_coords = coords[pairs[:, 1]]
        
        # Calculate displacement vectors
        dx = j_coords[:, 0] - i_coords[:, 0]
        dy = j_coords[:, 1] - i_coords[:, 1]
        distances = np.sqrt(dx**2 + dy**2)
        
        # Avoid division by zero for identical points
        non_zero_mask = distances > 1e-6
        valid_pairs = pairs[non_zero_mask]
        dx = dx[non_zero_mask]
        dy = dy[non_zero_mask]
        distances = distances[non_zero_mask]
        
        if len(valid_pairs) == 0:
            break
        
        # Calculate overlap and unit vectors
        overlaps = (min_distance - distances) / 2
        ux = dx / distances
        uy = dy / distances
        
        # Calculate movements
        move_x = ux * overlaps
        move_y = uy * overlaps
        
        # Accumulate movements for each point (some points might be in multiple pairs)
        movements = np.zeros_like(coords)
        movement_counts = np.zeros(n)
        
        # Add movements for i points (move away from j)
        np.add.at(movements[:, 0], valid_pairs[:, 0], -move_x)
        np.add.at(movements[:, 1], valid_pairs[:, 0], -move_y)
        np.add.at(movement_counts, valid_pairs[:, 0], 1)
        
        # Add movements for j points (move away from i)
        np.add.at(movements[:, 0], valid_pairs[:, 1], move_x)
        np.add.at(movements[:, 1], valid_pairs[:, 1], move_y)
        np.add.at(movement_counts, valid_pairs[:, 1], 1)
        
        # Average movements for points involved in multiple overlaps
        mask = movement_counts > 0
        movements[mask] /= movement_counts[mask, np.newaxis]
        
        # Apply movements with damping to prevent oscillation
        damping = 0.8
        coords += movements * damping
        
        # Check convergence
        max_movement = np.max(np.sqrt(np.sum(movements**2, axis=1)))
        if max_movement < tol:
            print(f"Converged after {iteration + 1} iterations (max movement: {max_movement:.3f})")
            break
    
    # Create new geometries from updated coordinates
    new_geometries = geometries.copy()
    for i, (x, y) in enumerate(coords):
        new_geometries.iloc[i] = Point(x, y)
    
    return new_geometries

def verify_distances(geometries, min_distance):
    """
    Verify the minimum distance between all points
    """
    coords = np.array([[geom.x, geom.y] for geom in geometries])
    tree = cKDTree(coords)
    
    # Find the closest pair
    distances, indices = tree.query(coords, k=2)  # k=2 to get closest neighbor (excluding self)
    min_found = np.min(distances[:, 1])  # [:, 1] to exclude distance to self (which is 0)
    
    return min_found

# Separate overlapping points
print("Separating overlapping points...")
new_geometries = separate_points_optimized(gdf.geometry, min_dist)

# Verify results
print("\nVerifying minimum distances...")
min_found = verify_distances(new_geometries, min_dist)
print(f"Minimum distance found: {min_found:.2f} meters")
print(f"Target minimum distance: {min_dist} meters")

# Update GeoDataFrame
gdf['geometry'] = new_geometries

# Convert back to WGS84
gdf = gdf.to_crs("EPSG:4326")

# Save
gdf.to_file("hi.geojson", driver="GeoJSON")