# AClimate V3 Cut Spatial Data 🌍✂️

## 🏷️ Version & Tags

![GitHub release (latest by date)](https://img.shields.io/github/v/release/CIAT-DAPA/aclimate_v3_cut_spatial_data) ![](https://img.shields.io/github/v/tag/CIAT-DAPA/aclimate_v3_cut_spatial_data)

**Tags:** `gis`, `raster`, `geoprocessing`, `python`, `geoserver`, `postgis`, `spatial_data`

---

## 📌 Introduction

Python package for advanced spatial data processing that enables:

- Raster clipping with shapefiles
- PostGIS integration for SQL-based clipping
- GeoServer connectivity for geometry extraction and clipping

**Use Cases:**

- Climate data processing (e.g., CHIRPS)
- Agricultural analysis by administrative zones
- Data extraction for specific areas of interest

---

## ✅ Prerequisites

- Python > 3.10
- PostGIS (optional, for PostGIS functionality)
- GeoServer (optional, for GeoServer integration)

## ⚙️ Installation

```bash
pip install git+https://github.com/CIAT-DAPA/aclimate_v3_cut_spatial_data
```

To install a specific version:

```bash
pip install git+https://github.com/CIAT-DAPA/aclimate_v3_cut_spatial_data@v0.0.1
```

## 🚀 Basic Usage

1. Clip with Shapefile

```python
from aclimate_v3_cut_spatial_data import get_clipper


input_raster = "path/raster.tif"
input_shape = "path/shapefile.shp"
output_file = "path/raster_result.tif"
clipper = get_clipper(input_raster, 'shape')
result = clipper.clip(input_shape)
result.rio.to_raster(output_file)

```

> [!NOTE]  
>  You must change the paths to the paths where the files are.

2. Clip with GeoServer

```python
from aclimate_v3_cut_spatial_data import get_clipper, GeoServerBasicAuth

input_raster = "path/raster.tif"
output_file = "path/raster_result.tif"
conn = GeoServerBasicAuth()  # Uses .env variables
clipper = get_clipper(input_raster, 'geoserver')
clipper.connection = conn

result = clipper.clip("workspace", "layer", "field_25") # If you want to clip by feature ID
result.rio.to_raster(output_file)

whole_result = clipper.clip("workspace", "layer") # If you want to clip by complete geometry
whole_result.rio.to_raster(output_file)

```

> [!NOTE]  
>  Required variables:
>
> - GEOSERVER_URL: Base URL of GeoServer (e.g., http://localhost:8080/geoserver)
> - GEOSERVER_USER: Username
> - GEOSERVER_PASSWORD: Password

3. Clip with PostGIS

```python
from sqlalchemy import create_engine
from aclimate_v3_cut_spatial_data import get_clipper

input_raster = "path/raster.tif"
output_file = "path/raster_result.tif"
database_url = os.getenv("DATABASE_URL") # Uses .env variables
engine = create_engine(database_url)
clipper = get_clipper(input_raster, 'postgis')
clipper.connection = engine
result = clipper.clip("SELECT geom FROM areas WHERE id=1")
result.rio.to_raster(output_file)

```

> [!NOTE]  
>  Required variables:
>
> - DATABASE_URL: Database connection string (e.g., postgresql://user:pass@localhost/db)

## 🔧 Configuration

### Environment Variables

Create .env file for GeoServer:

- Windows:

```bash
set GEOSERVER_URL=http://localhost:8080/geoserver
set GEOSERVER_USER=admin
set GEOSERVER_PASSWORD=secure_password
set DATABASE_URL=postgresql://user:pass@localhost/db
```

- Linux/Ubuntu:

```bash
export GEOSERVER_URL=http://localhost:8080/geoserver
export GEOSERVER_USER=admin
export GEOSERVER_PASSWORD=secure_password
export DATABASE_URL=postgresql://user:pass@localhost/db
```

## 🧪 Running Tests

```bash
# Install test requirements
pip install pytest pytest-mock

# Run tests
pytest tests/
```

## 🔄 CI/CD Pipeline Overview

### Workflow Architecture

Our GitHub Actions pipeline implements a three-stage deployment process:

```bash
Code Push → Test Stage → Merge Stage → Release Stage
```

## 📊 Project Structure

```bash
aclimate_v3_cut_spatial_data/
│
├── .github/
│ └── workflows/ # CI/CD pipeline configurations
├── src/
│   └── aclimate_v3_cut_spatial_data/
│       ├── clippers/          # Core clipping classes
│       ├── types/             # Type definitions
│       └── __init__.py        # Public interface
├── tests/
│   ├── test_data/             # Sample files
│   ├── test_shape_clipper.py
│   └── test_geoserver_clipper.py
├── pyproject.toml
└── requirements.txt # Package dependencies
```
