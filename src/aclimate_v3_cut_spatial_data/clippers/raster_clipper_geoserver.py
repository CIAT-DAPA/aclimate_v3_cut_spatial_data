import requests
from typing import Optional, Union
from ..types.raster_types import RioxarrayDataArray
from ..types.geometry_types import GeoServerConnection
from .raster_clipper import RioBaseClipper
import geopandas as gpd
from ..types.geometry_types import ShapelyGeometry
from shapely.geometry import shape
import logging
from io import BytesIO
import re

logger = logging.getLogger(__name__)

class RioGeoServerClipper(RioBaseClipper):

    def __init__(self, raster: RioxarrayDataArray):
        super().__init__(raster)
        self.connection: Optional[GeoServerConnection] = None
    
    def clip(
        self,
        feature_id: Optional[str] = None,
        cql_filter: Optional[str] = None,
        **kwargs
    ) -> 'RioxarrayDataArray':
        """
        Clips the raster using geometry retrieved from a GeoServer.

        Args:
            feature_id: Specific feature ID to use. If not provided, all geometries will be used.
            cql_filter: CQL filter to select specific subsets.
            **kwargs: Additional arguments passed to rio.clip()
        """
        if not self.connection:
            raise ValueError("No GeoServer connection has been established.")
        
        geometry = self._get_geoserver_geometry(self.connection, feature_id, cql_filter)
        
        return self.raster.rio.clip(
            [geometry],
            **kwargs
        )

    def _get_geoserver_geometry(
        self,
        conn: GeoServerConnection,
        workspace: str,
        layer: str,
        feature_id: Optional[str] = None,
        cql_filter: Optional[str] = None
    ) -> ShapelyGeometry:
        """Fetches geometry from GeoServer"""
        url = f"{conn.base_url}/{workspace}/ows"
        
        params = {
            'service': 'WFS',
            'version': '1.1.0',
            'request': 'GetFeature',
            'typeName': f"{layer}",
        }
        
        if feature_id:
            params['featureID'] = feature_id
        if cql_filter:
            params['cql_filter'] = cql_filter
        
        try:
            response = requests.get(
                url,
                params=params,
                auth=conn.auth
            )
            response.raise_for_status()
            
            gdf = gpd.read_file(BytesIO(response.content))
            
            # 1. Get CRS from WFS if not present in GeoDataFrame
            if gdf.crs is None:
                # Extract CRS from WFS XML response (included in WFS 1.1.0)
                wfs_xml = response.content.decode('utf-8')
                crs_match = re.search(r'srsName="([^"]+)"', wfs_xml)
                if crs_match:
                    crs_uri = crs_match.group(1)
                    # Convert EPSG URI to standard format (e.g., "EPSG:32616")
                    epsg_code = crs_uri.split(":")[-1]
                    gdf = gdf.set_crs(f"EPSG:{epsg_code}")
            
            # 2. If still no CRS, raise an explicit error
            if gdf.crs is None:
                raise ValueError(
                    "WFS response did not include CRS information. "
                    "Configure GeoServer to include srsName in the WFS response."
                )
            
            # 3. Reproject to raster CRS
            gdf = gdf.to_crs(self.raster.rio.crs)

            if len(gdf) == 0:
                raise ValueError("No features found with the given criteria.")
            
            if feature_id:
                return gdf.geometry.iloc[0]
            
            # If all features, return union of all geometries
            return gdf.geometry.union_all()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to GeoServer: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing geometry from GeoServer: {str(e)}")
            raise
