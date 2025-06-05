# Project-C-AR

## Problem + Project 
This quarter, our team chose Project C - (name of project) which focused on enhancing spatial data accuracy of mapped locations. Our main objective was to address issues relation to location correctness - specifically where we resolve spatial stacking, misplacement, and lack of contextual alignment based on the location address, metadata, category, and descriptive tags. Our project aims to reposition POIs and unstack locations to more accurately reflect the real-world spacial layout. 

## OKRs 
OKR #1: 
Objective: 
Enhance the accuracy and contextual relevance of map locations by identifying and improving incorrectly stacked or misrepresented points.

Key Results: 
* Identify and analyze stacked locations with >75% extraction accuracy from the total available dataset.
* Develop and evaluate a method to unstack or refine overlapping map locations, achieving at least 85% improvement in location separation precision.
* Implement a feedback mechanism from downstream systems/users to validate improved locations and achieve at least 80% positive accuracy feedback on refined locations.

OKR #2: 
Create an easy-to-use system that can find and fix wrong or confusing map locations (especially in oceans) using extra information.

Key Results: 
* Use extra details like place type, how busy the area is, or time of day to make location fixes more accurate (at least 70% correct and 80% complete).
* Check 5+ features like the environment around the location for additional contextual information.
* Leverage contextual data (e.g., address, metadata, user behavior) to refine 50% of stacked location clusters into more accurate distinct points.

## Approach 
During our analysis, we identified that densely populated areas such as shopping malls, small commercial complexes, and local markets often contained multiple stacked POIs. To resolve this, we implemented a spatial unstacking strategy by applying offsets to jitter points away from one another. Using a cKDTree, we were able to look at the points closest to the POI and jitter points away in those locations. This displacement preserved the relative spatial accuracy of these positions, while ensuring that the visual overlap was eliminated, enhancing the map readability and usability. 

To correct POIs positioned in random areas (roadways, water bodies, or open spaces), we introduced a point snapping system. This approach takes contextual data such as the POI's address and metadata, which then snaps the point to the nearest building if the contextual data matches. This snapping algorithm ensures that POIs are not in random locations, improving the readability of the map. 

## Conclusion 
