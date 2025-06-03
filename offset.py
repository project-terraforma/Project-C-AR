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