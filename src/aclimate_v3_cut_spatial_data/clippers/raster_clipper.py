from abc import ABC, abstractmethod
from typing import Optional, Any
from ..types.raster_types import RioxarrayDataArray
from ..types.geometry_types import GeometryInput, ShapelyGeometry

class RioBaseClipper(ABC):
    def __init__(self, raster: RioxarrayDataArray):
        self.raster = raster
        self._validate_crs()
    
    def _validate_crs(self) -> bool:
        """Validates that the raster has a defined CRS"""
        if not self.raster.rio.crs:
            raise ValueError("The raster must have a defined CRS")
        return True
    
    @abstractmethod
    def clip(
        self,
        geometry_input: GeometryInput,
        all_touched: bool = False,
        drop: bool = True,
        **kwargs
    ) -> RioxarrayDataArray:
        """Abstract method to be implemented by subclasses"""
        pass
    
    def _reproject_geometry(
        self,
        geometry: GeometryInput,
        target_crs: Optional[Any] = None
    ) -> ShapelyGeometry:
        """Reprojects the geometry to the raster CRS if necessary"""
        target_crs = target_crs or self.raster.rio.crs
        if geometry.crs and geometry.crs != target_crs:
            # Extract the first geometry from the reprojected GeoDataFrame
            return geometry.to_crs(target_crs).geometry.iloc[0]
        return geometry.geometry.iloc[0]
