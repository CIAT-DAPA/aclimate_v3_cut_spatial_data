from typing import Union, Protocol, runtime_checkable, Any
from pathlib import Path
import xarray as xr
import rioxarray
import numpy as np
import numpy.typing as npt

PathLike = Union[str, Path]
RasterArray = npt.NDArray[np.float32]

@runtime_checkable
class RioxarrayDataArray(Protocol):
    rio: Any
    values: RasterArray
    attrs: dict
    
    def sel(self, **kwargs) -> xr.DataArray: ...
    def clip_box(self, **kwargs) -> xr.DataArray: ...