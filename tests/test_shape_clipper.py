# test_shape_clipper.py actualizado
import pytest
from pathlib import Path
import os
import rioxarray
import xarray
from aclimate_v3_cut_spatial_data import get_clipper
import geopandas as gpd
from shapely.geometry import box

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"

@pytest.fixture
def sample_raster(test_data_dir):
    raster_path = test_data_dir / "sample_raster.tif"
    return rioxarray.open_rasterio(raster_path)

@pytest.fixture
def sample_shapefile(test_data_dir):
    return os.path.join(test_data_dir, "shape", "limite_nacional.shp")

@pytest.fixture
def sample_geodataframe():
    geometry = [box(0, 0, 10, 10)]
    return gpd.GeoDataFrame(geometry=geometry, crs="EPSG:4326")

def test_shape_clipper_with_shapefile(sample_raster, sample_shapefile, tmp_path):
    clipper = get_clipper(sample_raster, 'shape')
    output_path = tmp_path / "output_shape.tif"
    
    result = clipper.clip(sample_shapefile)
    result.rio.to_raster(output_path)
    
    assert output_path.exists()
    assert result.rio.shape[0] <= sample_raster.rio.shape[0]
    assert result.rio.shape[1] <= sample_raster.rio.shape[1]

def test_shape_clipper_with_geodataframe(sample_raster, sample_geodataframe, tmp_path):
    clipper = get_clipper(sample_raster, 'shape')
    output_path = tmp_path / "output_gdf.tif"
    
    result = clipper.clip(sample_geodataframe)
    result.rio.to_raster(output_path)
    
    assert output_path.exists()
    assert isinstance(result, xarray.DataArray)
    assert hasattr(result, 'rio')