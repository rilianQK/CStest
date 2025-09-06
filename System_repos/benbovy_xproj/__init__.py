from __future__ import annotations

import xarray as xr

from .accessor import ProjAccessor, register_accessor
from .crs_utils import format_compact_cf, format_full_cf_gdal
from .index import CRSIndex
from .mixins import ProjAccessorMixin, ProjIndexMixin
from .utils import Frozen, FrozenDict

__version__ = "0.1.0"
__all__ = [
    "ProjAccessor",
    "register_accessor",
    "CRSIndex",
    "ProjAccessorMixin",
    "ProjIndexMixin",
    "format_compact_cf",
    "format_full_cf_gdal",
    "Frozen",
    "FrozenDict",
]

_ProjAccessor = ProjAccessor  # noqa: F401

xr.register_dataset_accessor("proj")(ProjAccessor)
xr.register_dataarray_accessor("proj")(ProjAccessor)