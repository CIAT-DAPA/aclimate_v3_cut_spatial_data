from typing import Union, Optional
import geopandas as gpd
from ..types.geometry_types import ShapelyGeometry, PostGISConnection
from .raster_clipper import RioBaseClipper
import sqlalchemy
from ..types.raster_types import RioxarrayDataArray

class RioPostGISClipper(RioBaseClipper):
    def __init__(self, raster: RioxarrayDataArray, connection: Optional[PostGISConnection] = None):
        super().__init__(raster)
        self.connection = connection
    
    def clip(
        self,
        geometry_input: Union[PostGISConnection, str],
        query: Optional[str] = None,
        all_touched: bool = False,
        drop: bool = True,
        **kwargs
    ) -> RioxarrayDataArray:
        """
        Clips the raster using geometries from a PostGIS database.
        
        Args:
            geometry_input: Either a PostGIS connection or an SQL query string.
            query: SQL query if geometry_input is a connection.
            all_touched: Include pixels that touch the geometry.
            drop: Remove pixels outside the geometry.
        """
        conn, query = self._resolve_inputs(geometry_input, query)
        gdf = self._execute_query(conn, query)
        geometry = self._reproject_geometry(gdf)
        
        return self.raster.rio.clip(
            [geometry],
            all_touched=all_touched,
            drop=drop,
            **kwargs
        )
    
    def _resolve_inputs(
        self,
        geometry_input: Union[PostGISConnection, str],
        query: Optional[str]
    ) -> tuple[PostGISConnection, str]:
        if isinstance(geometry_input, str):
            if not self.connection:
                raise ValueError("PostGIS connection is required.")
            return self.connection, geometry_input
        elif hasattr(geometry_input, 'execute'):
            if not query:
                raise ValueError("SQL query is required.")
            return geometry_input, query
        else:
            raise TypeError("Input must be a PostGIS connection or an SQL query string.")
    
    def _execute_query(self, conn: PostGISConnection, query: str) -> gpd.GeoDataFrame:
        """Executes a PostGIS query and returns a GeoDataFrame."""
        # Specific implementation for your PostGIS connection
        # Generic example:
        return gpd.read_postgis(query, conn)
