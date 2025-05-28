from typing import Union, Protocol, runtime_checkable, Any
from shapely.geometry import base, Polygon, MultiPolygon
import geopandas as gpd
import requests
from dataclasses import dataclass
import os
from dotenv import load_dotenv

ShapelyGeometry = Union[base.BaseGeometry, Polygon, MultiPolygon]

@runtime_checkable
class PostGISConnection(Protocol):
    def execute(self, query: str) -> Any: ...
    def fetchall(self) -> list[Any]: ...

class GeometryInput:
    def to_crs(self, crs: Any) -> 'GeometryInput': ...
    def to_shapely(self) -> ShapelyGeometry: ...
    @property
    def crs(self) -> Any: ...

@runtime_checkable
class GeoServerConnection(Protocol):
    base_url: str
    auth: tuple

    def get_feature(self, feature_id: str) -> 'GeometryInput': ...

@dataclass
class GeoServerBasicAuth(GeoServerConnection):
    """
    GeoServer connection that loads configuration from environment variables.
    
    Required variables:
    - GEOSERVER_URL: Base URL of GeoServer (e.g., http://localhost:8080/geoserver)
    - GEOSERVER_WORKSPACE: Name of the workspace
    - GEOSERVER_LAYER: Name of the layer
    - GEOSERVER_USER: Username
    - GEOSERVER_PASSWORD: Password
    """
    base_url: str = ""
    auth: tuple = ("", "")

    def __init__(self):
        load_dotenv()
        self.base_url: str = os.getenv('GEOSERVER_URL')
        self.auth: tuple = (
            os.getenv('GEOSERVER_USER'), 
            os.getenv('GEOSERVER_PASSWORD')
        )
        """Validate that all required environment variables are set"""
        if not all([self.base_url, self.auth[0], self.auth[1]]):
            raise ValueError(
                "Missing required environment variables: "
                "GEOSERVER_URL, GEOSERVER_USER, GEOSERVER_PASSWORD"
            )

    def get_feature(self, feature_id: str):
        """Gets a specific feature"""
        return {
            'type': 'feature',
            'id': feature_id,
            'connection': self
        }
