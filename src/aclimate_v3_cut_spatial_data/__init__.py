import rioxarray
from .clippers import RioShapeClipper, RioPostGISClipper, RioGeoServerClipper
from .types import RioxarrayDataArray, GeoServerBasicAuth
from typing import Union

def open_raster(raster_path: str) -> RioxarrayDataArray:
    """Opens a raster using rioxarray"""
    xds = rioxarray.open_rasterio(raster_path)
    if not xds.rio.crs:
        raise ValueError("The raster must have a defined CRS")
    return xds

def get_clipper(
    raster: Union[str, 'RioxarrayDataArray'],
    clip_type: str = 'auto'
) -> Union[RioShapeClipper, RioPostGISClipper, RioGeoServerClipper]:
    """
    Factory to get the appropriate clipper
    
    Args:
        raster: Path to the raster file or a rioxarray DataArray
        clip_type: 'shape', 'postgis', 'geoserver', or 'auto'
    """
    if isinstance(raster, str):
        raster = open_raster(raster)
    
    if clip_type == 'auto':
        # Autodetection logic
        return RioShapeClipper(raster)
    elif clip_type == 'shape':
        return RioShapeClipper(raster)
    elif clip_type == 'postgis':
        return RioPostGISClipper(raster)
    elif clip_type == 'geoserver':
        return RioGeoServerClipper(raster)
    else:
        raise ValueError(f"Unsupported clip type: {clip_type}")

