import pytest
from unittest.mock import Mock, patch
import rioxarray
import geopandas as gpd
from shapely.geometry import box
import xarray
from aclimate_v3_cut_spatial_data import get_clipper, GeoServerBasicAuth
from io import BytesIO
import os

@pytest.fixture
def mock_geoserver_response():
    """Mejorado para devolver un GeoDataFrame con CRS"""
    geometry = box(0, 0, 10, 10)
    gdf = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
    
    # Mock más realista del XML de respuesta WFS
    wfs_xml = f"""<?xml version="1.0" ?>
        <wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs" 
        xmlns:gml="http://www.opengis.net/gml" 
        xmlns:ogc="http://www.opengis.net/ogc" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd"
        srsName="EPSG:4326">
        <gml:featureMember>
            <feature fid="1">
                <geometry>{geometry.wkt}</geometry>
            </feature>
        </gml:featureMember>
        </wfs:FeatureCollection>"""
    
    return BytesIO(wfs_xml.encode('utf-8'))

@pytest.fixture
def sample_raster():
    """Raster de prueba con CRS definido"""
    # Crear un pequeño raster en memoria para pruebas
    data = xarray.DataArray(
        [[1, 2], [3, 4]],
        dims=("y", "x"),
        coords={"y": [0, 1], "x": [0, 1]},
        attrs={"crs": "EPSG:4326"}
    )
    return data.rio.write_crs("EPSG:4326")

@patch('geopandas.read_file')
@patch('requests.get')
@patch.dict(os.environ, {
    "GEOSERVER_URL": "http://mock-server",
    "GEOSERVER_USER": "user",
    "GEOSERVER_PASSWORD": "pass"
})
def test_geoserver_clipper(mock_get, mock_read, sample_raster, mock_geoserver_response, tmp_path):
    # Configurar mocks
    mock_response = Mock()
    mock_response.content = mock_geoserver_response.getvalue()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Crear un GeoDataFrame mock con CRS
    geometry = box(0, 0, 10, 10)
    mock_gdf = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
    mock_read.return_value = mock_gdf
    
    # Configurar conexión GeoServer
    geoserver_conn = GeoServerBasicAuth()
    
    # Probar el clipper
    clipper = get_clipper(sample_raster, 'geoserver')
    clipper.connection = geoserver_conn
    
    output_path = tmp_path / "output_geoserver.tif"
    result = clipper.clip("test_ws", "test_layer",  feature_id="1")
    result.rio.to_raster(output_path)
    
    # Verificaciones
    assert output_path.exists()
    assert mock_get.called
    assert mock_read.called
    assert result.rio.crs == sample_raster.rio.crs

def test_geoserver_clipper_no_connection(sample_raster):
    clipper = get_clipper(sample_raster, 'geoserver')
    
    with pytest.raises(ValueError, match="No GeoServer connection"):
        clipper.clip("test_ws", "test_layer",)

@patch('geopandas.read_file')
@patch('requests.get')
def test_geoserver_clipper_cql_filter(mock_get, mock_read, sample_raster, mock_geoserver_response):
    # Configurar mocks
    mock_response = Mock()
    mock_response.content = mock_geoserver_response.getvalue()
    mock_get.return_value = mock_response
    
    geometry = box(0, 0, 10, 10)
    mock_gdf = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
    mock_read.return_value = mock_gdf
    
    # Configurar conexión
    geoserver_conn = GeoServerBasicAuth()
    geoserver_conn.base_url = "http://mock-geoserver"
    
    # Probar el clipper
    clipper = get_clipper(sample_raster, 'geoserver')
    clipper.connection = geoserver_conn
    
    clipper.clip("test_ws", "test_layer", cql_filter="NAME='Test'")
    
    # Verificar que se usó el filtro CQL
    assert mock_get.call_args[1]['params']['cql_filter'] == "NAME='Test'"