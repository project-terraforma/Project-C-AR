# POIs to Buildings GUI

This is an interactive web-based tool built with Flask, Leaflet, DuckDB, and GeoPandas for **snapping POIs (Points of Interest) to nearby buildings** within a user-defined bounding box.

## Features

- 🌐 Web-based map UI with Leaflet.js
- ✏️ Draw bounding boxes to define the area of interest
- 📦 Automatically downloads and filters POIs and building data from **Overture Maps**
- 📍 Uses spatial joins and heuristics to assign POIs to buildings
- 🗂️ Outputs a new `GeoJSON` file showing snapped POI positions
- 📊 Visual side-by-side comparison of POIs before and after snapping

---

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/pois-to-buildings-gui.git
cd pois-to-buildings-gui
```

### 2. Install dependencies
Make sure you have Python 3.8+ installed.

```bash
pip install flask flask-cors geopandas duckdb shapely
```

> If you’re on Ubuntu and need `tkinter` or `gdal` for `geopandas`, install them using:
> ```bash
> sudo apt-get install python3-tk gdal-bin libgdal-dev
> ```

---

## 🚀 Usage

### 1. Start the Flask App
```bash
python poistobuildingsgui.py
```

This will start a development server at `http://localhost:8000`.

### 2. Open in Browser
Navigate to [http://localhost:8000](http://localhost:8000).

- 🗺️ Draw a bounding box over your area of interest.
- ▶️ Click **Run Snapping** to trigger the logic.
- 📁 View side-by-side maps of original and snapped POIs.

---

## 📂 File Structure

```
.
├── poistobuildingsgui.py       # Main Flask + snapping logic
├── bbox.json                   # Stores last drawn bounding box
├── static/
│   └── geojson/
│       ├── pois.geojson        # Raw POIs
│       ├── buildings.geojson   # Raw building geometries
│       └── poistobuildings.geojson  # Output with snapped POIs
```

---

## 📤 Output

- **Snapped POIs** are saved to: `static/geojson/poistobuildings.geojson`
- You can download or reuse this file in GIS tools like QGIS or kepler.gl.

---

## 🧠 Logic Overview

1. **Bounding Box Input**  
   User defines the area using a Leaflet rectangle.

2. **Data Query via DuckDB**  
   Uses Overture Maps Parquet datasets directly from S3.

3. **Spatial Joins & Matching**  
   - POIs already inside buildings are marked.
   - Remaining POIs are snapped to:
     - buildings with matching names, or
     - nearest intersecting buildings, or
     - closest building centroid

4. **Result Exported**  
   A new `GeoJSON` is created with updated POI geometries.

---

## ✅ Requirements

- Python 3.8+
- Internet connection (for loading Overture data via DuckDB S3 access)
- Web browser

---

## 📝 Notes

- The system uses **UTM Zone 10N (EPSG:32610)** for accurate buffering/snapping, then converts back to WGS84 (EPSG:4326) for export.
- Make sure your environment supports GUI windows (required for `tkinter`, if used in extensions).

---

## 📄 License

MIT License.
