from os import PathLike
from pathlib import Path
from typing import Union
import geopandas as gpd
import rioxarray
from ..types.geometry_types import ShapelyGeometry
from .raster_clipper import RioBaseClipper
from ..types.raster_types import RioxarrayDataArray

class RioShapeClipper(RioBaseClipper):
    def clip(
        self,
        geometry_input: Union[PathLike, gpd.GeoDataFrame, ShapelyGeometry],
        all_touched: bool = False,
        drop: bool = True,
        invert: bool = False,
        **kwargs
    ) -> RioxarrayDataArray:
        """
        Clips the raster using rioxarray with shapefile geometries.
        
        Args:
            geometry_input: Can be a path to a shapefile, a GeoDataFrame, or a Shapely geometry
            all_touched: Include pixels that touch the geometry (not just center)
            drop: Remove pixels outside the geometry
            invert: Invert the mask (clip what's outside)
        """
        geometry = self._resolve_geometry(geometry_input)
        
        clipped = self.raster.rio.clip(
            [geometry],
            all_touched=all_touched,
            drop=drop,
            invert=invert,
            **kwargs
        )
        
        return clipped
    
    def _resolve_geometry(
        self,
        input_geom: Union[PathLike, gpd.GeoDataFrame, ShapelyGeometry]
    ) -> ShapelyGeometry:
        """Converts various input types to a Shapely geometry"""
        if isinstance(input_geom, (str, Path)):
            gdf = gpd.read_file(input_geom)
            return self._reproject_geometry(gdf)
        elif isinstance(input_geom, gpd.GeoDataFrame):
            return self._reproject_geometry(input_geom)
        elif isinstance(input_geom, ShapelyGeometry):
            return input_geom  # Assumes same CRS as the raster
        else:
            raise TypeError(f"Unsupported geometry type: {type(input_geom)}")
