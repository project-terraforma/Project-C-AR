import os
import json
import pandas as pd
import geopandas as gpd
from flask import Flask, request, send_from_directory, Response
from flask_cors import CORS
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree
import duckdb

OUTPUT_DIR = os.path.join("static", "geojson")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def draw_bbox_page():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Draw Bounding Box</title>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
        <style>
            html, body, #map { height: 100%; margin: 0; padding: 0; }
            #run-btn {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                padding: 10px 20px;
                background: white;
                border: 1px solid #aaa;
                cursor: pointer;
            }
            #loading {
                display: none;
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(255,255,255,0.8);
                font-size: 24px;
                justify-content: center;
                align-items: center;
                z-index: 2000;
            }
            #loading.active { display: flex; }
        </style>
    </head>
    <body>
        <div id="loading">⏳ Running snapping logic...</div>
        <div id="map"></div>
        <div id="run-btn">▶️ Run Snapping</div>

        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
        <script>
            const map = L.map('map').setView([37.294, -121.78], 18);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
            const drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);

            const drawControl = new L.Control.Draw({
                draw: {
                    marker: false, polyline: false, polygon: false,
                    circle: false, circlemarker: false, rectangle: true
                },
                edit: { featureGroup: drawnItems }
            });
            map.addControl(drawControl);

            let lastBbox = null;
            map.on('draw:created', function (e) {
                drawnItems.clearLayers();
                drawnItems.addLayer(e.layer);
                const bounds = e.layer.getBounds();
                lastBbox = {
                    xmin: bounds.getWest(), ymin: bounds.getSouth(),
                    xmax: bounds.getEast(), ymax: bounds.getNorth()
                };
                fetch('/bbox', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(lastBbox)
                });
                alert("Bounding box saved.");
            });

            document.getElementById("run-btn").addEventListener("click", function () {
                if (!lastBbox) {
                    alert("Please draw a bounding box first.");
                    return;
                }

                document.getElementById("loading").classList.add("active");

                fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: "run_snapping" })
                })
                .then(res => res.text())
                .then(() => {
                    window.location.href = "/results";
                })
                .catch(err => {
                    alert("Error running snapping logic.");
                    document.getElementById("loading").classList.remove("active");
                });
            });
        </script>
    </body>
    </html>"""
    return Response(html, mimetype="text/html")

@app.route("/results")
def result_map():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Snapping Results</title>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <style>
            body, html { margin: 0; height: 100%; display: flex; flex-direction: column; }
            #maps { flex: 1; display: flex; }
            #map-before, #map-after { flex: 1; }
            #footer {
                padding: 10px;
                text-align: center;
                border-top: 1px solid #ccc;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="maps">
            <div id="map-before"></div>
            <div id="map-after"></div>
        </div>
        <div id="footer">
            <button onclick="location.href='/'">🔙 Back to Drawing</button>
        </div>

        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
            function loadMap(id, center, zoom) {
                const map = L.map(id).setView(center, zoom);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19
                }).addTo(map);
                return map;
            }

            function loadLayer(map, url, style, popupProp) {
                fetch(url)
                    .then(res => res.json())
                    .then(data => {
                        const layer = L.geoJSON(data, {
                            style,
                            onEachFeature: (feature, layer) => {
                                if (popupProp && feature.properties[popupProp]) {
                                    layer.bindPopup(feature.properties[popupProp]);
                                }
                            },
                            pointToLayer: (f, latlng) => L.circleMarker(latlng, style)
                        });
                        layer.addTo(map);
                        map.fitBounds(layer.getBounds());
                    });
            }

            const mapBefore = loadMap('map-before', [37.294, -121.78], 18);
            const mapAfter = loadMap('map-after', [37.294, -121.78], 18);

            loadLayer(mapBefore, '/geojson/pois.geojson', { color: 'blue', radius: 5 }, 'name');
            loadLayer(mapBefore, '/geojson/buildings.geojson', { color: 'gray' });

            loadLayer(mapAfter, '/geojson/poistobuildings.geojson', { color: 'red', radius: 5 }, 'name');
            loadLayer(mapAfter, '/geojson/buildings.geojson', { color: 'gray' });
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")

@app.route('/geojson/<path:filename>')
def serve_geojson(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route('/bbox', methods=['POST'])
def receive_bbox():
    data = request.get_json()
    with open("bbox.json", "w") as f:
        json.dump(data, f)
    print("✅ Received bounding box:", data)
    return "OK"


@app.route('/run', methods=['POST'])
def trigger_snapping():
    print("🚀 Snapping triggered!", flush=True)
    try:
        run_snapping_from_bbox()
        return "✅ Snapping logic completed."
    except Exception as e:
        print(f"❌ ERROR: {e}", flush=True)
        return f"Error: {e}", 500


def run_snapping_from_bbox():
    print("🔄 Running snapping logic...", flush=True)

    if not os.path.exists("bbox.json"):
        print("❌ No bounding box found. Exiting snapping.")
        return

    with open("bbox.json", "r") as f:
        bbox = json.load(f)

    xmin, xmax = bbox["xmin"], bbox["xmax"]
    ymin, ymax = bbox["ymin"], bbox["ymax"]

    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL spatial;")
    con.execute("LOAD spatial;")

    print("🚧 Querying data...", flush=True)

    # Save buildings.geojson
    con.execute(f"""
    COPY (
        SELECT id, level, height, names.primary AS primary_name,
               sources[1].dataset AS primary_source, geometry
        FROM read_parquet(
            's3://overturemaps-us-west-2/release/2025-05-21.0/theme=buildings/type=*/*',
            hive_partitioning=1
        )
        WHERE bbox.xmin > {xmin} AND bbox.xmax < {xmax}
          AND bbox.ymin > {ymin} AND bbox.ymax < {ymax}
    ) TO '{os.path.join(OUTPUT_DIR, 'buildings.geojson')}' (FORMAT GDAL, DRIVER 'GeoJSON');
    """)

    # Save pois.geojson
    con.execute(f"""
    COPY (
        SELECT id, names.primary AS name, CAST(addresses AS JSON) AS addresses,
               confidence, geometry
        FROM read_parquet(
            's3://overturemaps-us-west-2/release/2025-04-23.0/theme=places/type=place/*',
            hive_partitioning=1
        )
        WHERE bbox.xmin > {xmin} AND bbox.xmax < {xmax}
          AND bbox.ymin > {ymin} AND bbox.ymax < {ymax}
    ) TO '{os.path.join(OUTPUT_DIR, 'pois.geojson')}' (FORMAT GDAL, DRIVER 'GeoJSON');
    """)

    print("✅ Query complete.", flush=True)

    pois = gpd.read_file(os.path.join(OUTPUT_DIR, "pois.geojson")).to_crs(epsg=32610)
    buildings = gpd.read_file(os.path.join(OUTPUT_DIR, "buildings.geojson")).to_crs(epsg=32610)

    if pois.empty or buildings.empty:
        print("❗ Either POIs or Buildings are empty. Exiting.")
        return

    within = gpd.sjoin(pois, buildings, how="left", predicate="within").reset_index()
    poi_inside_flags = within.groupby("index")["index_right"].apply(lambda x: x.notna().any())
    pois["inside_building"] = pois.index.to_series().map(poi_inside_flags).fillna(False)

    outside_pois = pois[~pois["inside_building"]].copy()
    buffered = outside_pois.copy()
    buffered["geometry"] = buffered.geometry.buffer(50)
    candidates = gpd.sjoin(buildings, buffered, how="inner", predicate="intersects")

    name_to_buildings = {}
    for _, row in buildings.iterrows():
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
            match_candidates["dist"] = match_candidates.geometry.centroid.distance(poi_geom)
            return match_candidates.sort_values("dist").iloc[0].geometry.centroid

        nearby_centroids = str_tree.query(poi_geom.buffer(200))
        valid_centroids = [c for c in nearby_centroids if isinstance(c, BaseGeometry)]

        if valid_centroids:
            nearest = min(valid_centroids, key=lambda c: poi_geom.distance(c))
            best_building = buildings.loc[centroid_to_building[nearest]]
            return best_building.geometry.centroid

        return poi_geom

    outside_pois["new_geometry"] = outside_pois.apply(find_best_building_optimized, axis=1)
    inside_pois = pois[pois["inside_building"]].copy()
    inside_pois["new_geometry"] = inside_pois.geometry

    final = pd.concat([inside_pois, outside_pois], ignore_index=True)
    final = final.set_geometry("new_geometry").set_crs(epsg=32610).to_crs(epsg=4326)
    final = final.drop(columns=["geometry", "inside_building"]).rename(columns={"new_geometry": "geometry"})
    final = final.set_geometry("geometry")

    final.to_file(os.path.join(OUTPUT_DIR, "poistobuildings.geojson"), driver="GeoJSON")
    print("✅ Snapping complete. Output saved to `static/geojson/poistobuildings.geojson`.")


if __name__ == "__main__":
    print("🌐 Flask app starting at http://localhost:8000")
    app.run(host="localhost", port=8000, debug=True)
