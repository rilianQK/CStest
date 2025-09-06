from __future__ import annotations

import functools
import warnings
from collections.abc import Hashable, Mapping
from typing import TYPE_CHECKING, Any, TypeVar

import xarray as xr

from .crs_utils import format_compact_cf
from .index import CRSIndex
from .mixins import ProjAccessorMixin, ProjIndexMixin
from .utils import Frozen, FrozenDict

if TYPE_CHECKING:
    import pyproj

T_AccessorClass = TypeVar("T_AccessorClass")


def register_accessor(accessor_cls: Any) -> T_AccessorClass:
    """Decorator for registering a geospatial, CRS-dependent Xarray
    (Dataset and/or DataArray) accessor.

    Parameters
    
    accessor_cls : class
        A Python class that has been decorated with
        :py:func:`xarray.register_dataset_accessor` and/or
        :py:func:`xarray.register_dataarray_accessor`.
        It is important that this decorator is applied on top of
        those Xarray decorators.
    """
    GeoAccessorRegistry.register_accessor(accessor_cls)
    return accessor_cls


def either_dict_or_kwargs(
    positional: Any, keyword: Any, func_name: Any
) -> Mapping[Hashable, Any]:
    """Resolve combination of positional and keyword arguments.

    Based on xarray's ``either_dict_or_kwargs``."""
    if positional and keyword:
        raise ValueError(
            f"Cannot specify both positional and keyword arguments to {func_name}"
        )
    elif positional:
        if not isinstance(positional, Mapping):
            raise TypeError(
                f"First argument to {func_name} must be a dict-like, not {type(positional)}"
            )
        return positional
    else:
        return keyword


def is_crs_aware(index: Any) -> bool:
    """Determine whether a given xarray Index is CRS-aware by checking if it is an instance of ProjIndexMixin or has the method "_proj_get_crs"."""
    return isinstance(index, ProjIndexMixin) or hasattr(index, "_proj_get_crs")


class CRSProxy:
    """A proxy for a CRS(-aware) indexed coordinate."""

    def __init__(self, obj: Any, coord_name: Any, crs: Any) -> None:
        self._obj = obj
        self._coord_name = coord_name
        self._crs = crs

    @property
    def crs(self) -> pyproj.CRS:
        """Return the coordinate reference system as a :class:`pyproj.CRS` object."""
        return self._crs


class GeoAccessorRegistry:
    """A registry of 3rd-party geospatial Xarray accessors."""

    _accessor_names: dict[type[xr.Dataset] | type[xr.DataArray], set[str]] = {}

    @classmethod
    def get_accessors(cls, xr_obj: Any) -> list[Any]:
        """Retrieve a list of valid accessor objects from an xarray Dataset or DataArray based on predefined accessor names, excluding any that are instances of xr.DataArray."""
        accessors = []
        for xr_type, names in cls._accessor_names.items():
            if isinstance(xr_obj, xr_type):
                for name in names:
                    if hasattr(xr_obj, name):
                        accessor = getattr(xr_obj, name)
                        if not isinstance(accessor, xr.DataArray):
                            accessors.append(accessor)
        return accessors

    @classmethod
    def register_accessor(cls, accessor_cls: Any) -> None:
        """Register an Xarray Dataset or DataArray accessor class to a target class by updating the accessor names mapping for the respective Xarray classes."""
        if hasattr(accessor_cls, "_accessor_target"):
            target = accessor_cls._accessor_target
            if target not in cls._accessor_names:
                cls._accessor_names[target] = set()
            cls._accessor_names[target].add(accessor_cls._accessor_name)


class ProjAccessor:
    """Xarray `.proj` extension entry-point."""

    def __init__(self, obj: Any) -> None:
        self._obj = obj
        self._crs_indexes_cache = None
        self._crs_aware_indexes_cache = None

    def __call__(self, coord_name: Any) -> CRSProxy:
        """Select a given CRS by coordinate name.

        Parameter
        
        coord_name : Hashable
            Either the name of a (scalar) spatial reference coordinate with a
            :py:class:`~xproj.CRSIndex` or the name of a coordinate with an
            index that implements XProj's CRS interface.

        Returns
        
        proxy
            A proxy accessor for a single CRS.
        """
        if coord_name in self.crs_indexes:
            crs_index = self._get_crs_index(coord_name)
            return CRSProxy(self._obj, coord_name, crs_index.crs)
        elif coord_name in self.crs_aware_indexes:
            index = self.crs_aware_indexes[coord_name]
            crs = index._proj_get_crs() if hasattr(index, "_proj_get_crs") else None
            if crs is None:
                raise ValueError(f"Coordinate '{coord_name}' has no CRS defined")
            return CRSProxy(self._obj, coord_name, crs)
        else:
            raise ValueError(
                f"Coordinate '{coord_name}' has no CRSIndex and is not CRS-aware"
            )

    def _cache_all_crs_indexes(self) -> None:
        """Cache all CRSIndex objects and CRS-aware Index objects from the object's xindexes into separate dictionaries for quick access.
get both CRSIndex objects and CRS-aware Index objects in cache"""
        crs_indexes = {}
        crs_aware_indexes = {}
        
        for coord_name, index in self._obj.xindexes.items():
            if isinstance(index, CRSIndex):
                crs_indexes[coord_name] = index
            elif is_crs_aware(index):
                crs_aware_indexes[coord_name] = index
        
        self._crs_indexes_cache = FrozenDict(crs_indexes)
        self._crs_aware_indexes_cache = FrozenDict(crs_aware_indexes)

    def _get_crs_index(self, coord_name: Any) -> CRSIndex:
        """Retrieve the CRSIndex associated with a specified coordinate name in a Dataset or DataArray, ensuring the coordinate exists, is scalar, and has a valid CRSIndex.
Get a nice error message when trying to access a spatial reference
coordinate with a CRSIndex using an arbitrary name."""
        if coord_name not in self._obj.coords:
            raise ValueError(f"Coordinate '{coord_name}' not found")
        
        coord = self._obj.coords[coord_name]
        if coord.ndim != 0:
            raise ValueError(f"Coordinate '{coord_name}' must be scalar")
        
        if coord_name not in self.crs_indexes:
            raise ValueError(f"Coordinate '{coord_name}' has no CRSIndex")
        
        return self.crs_indexes[coord_name]

    def _update_crs_info(
        self, spatial_ref: Any, func: Any
    ) -> xr.DataArray | xr.Dataset:
        """Update the Coordinate Reference System (CRS) information in an xarray object by applying a given function to specified spatial reference coordinates or all CRS indexes if none are specified."""
        if spatial_ref is None:
            spatial_refs = list(self.crs_indexes.keys())
        else:
            spatial_refs = [spatial_ref]
        
        obj = self._obj
        for ref in spatial_refs:
            crs_index = self._get_crs_index(ref)
            attrs = func(crs_index.crs)
            obj = obj.assign_coords({ref: obj.coords[ref].assign_attrs(**attrs)})
        
        return obj

    def assert_one_crs_index(self) -> None:
        """Raise an `AssertionError` if no or multiple CRS-indexed coordinates
        are found in the Dataset or DataArray."""
        if len(self.crs_indexes) == 0:
            raise AssertionError("No CRS-indexed coordinates found")
        elif len(self.crs_indexes) > 1:
            raise AssertionError(f"Multiple CRS-indexed coordinates found: {list(self.crs_indexes.keys())}")

    def assign_crs(
        self,
        spatial_ref_crs: Any = None,
        allow_override: Any = False,
        **spatial_ref_crs_kwargs: Any,
    ) -> xr.DataArray | xr.Dataset:
        """Assign one or more spatial reference coordinate variables, each with
        a given coordinate reference system (CRS).

        Doesn't trigger any coordinate transformation or data resampling.

        Parameters
        
        spatial_ref_crs : dict-like or None, optional
            A dict where the keys are the names of the (scalar) coordinate variables
            and values target CRS in any format accepted by
            :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>` such
            as an authority string (e.g. ``"EPSG:4326"``), EPSG code (e.g. ``4326``) or
            a WKT string.
            If the coordinate(s) doesn't exist it will be created.
        allow_override : bool, default False
            Allow to replace the index if the coordinates already have an index.
        **spatial_ref_crs_kwargs : optional
            The keyword arguments form of ``spatial_ref_crs``.
            One of ``spatial_ref_crs`` or ``spatial_ref_crs_kwargs`` must be provided.

        Returns
        
        Dataset or DataArray
            A new Dataset or DataArray object with new or updated
            :term:`spatial reference coordinate` variables.
        """
        import pyproj

        spatial_ref_crs = either_dict_or_kwargs(
            spatial_ref_crs, spatial_ref_crs_kwargs, "assign_crs"
        )
        
        obj = self._obj
        for coord_name, crs_input in spatial_ref_crs.items():
            crs = pyproj.CRS.from_user_input(crs_input)
            
            if coord_name in obj.coords:
                coord = obj.coords[coord_name]
                if coord.ndim != 0:
                    raise ValueError(f"Coordinate '{coord_name}' must be scalar")
                
                if coord_name in obj.xindexes and not allow_override:
                    raise ValueError(
                        f"Coordinate '{coord_name}' already has an index. "
                        "Use allow_override=True to replace it."
                    )
                
                obj = obj.set_xindex(coord_name, CRSIndex(crs))
            else:
                obj = obj.assign_coords({coord_name: xr.DataArray(0, attrs={})})
                obj = obj.set_xindex(coord_name, CRSIndex(crs))
            
            for accessor in GeoAccessorRegistry.get_accessors(obj):
                if isinstance(accessor, ProjAccessorMixin):
                    obj = accessor._proj_set_crs(coord_name, crs)
        
        return obj

    def clear_crs_info(self, spatial_ref: Any = None) -> xr.DataArray | xr.Dataset:
        """Convenient method to clear all attributes of one or all spatial
        reference coordinates.

        Parameters
        
        spatial_ref : Hashable, optional
            The name of a :term:`spatial reference coordinate`. If not provided (default),
            CRS information will be cleared for all spatial reference coordinates found in
            the Dataset or DataArray. Each spatial reference coordinate must already have
            a :py:class:`~xproj.CRSIndex` associated.

        Returns
        
        Dataset or DataArray
            A new Dataset or DatArray object with attributes cleared for one or all
            spatial reference coordinates.

        See Also
        
        Dataset.proj.write_crs_info
        DataArray.proj.write_crs_info
        """
        def clear_func(crs: Any) -> dict[str, Any]:
            return {}
        
        return self._update_crs_info(spatial_ref, clear_func)

    @property
    def crs(self) -> pyproj.CRS | None:
        """Return the coordinate reference system as a :py:class:`pyproj.crs.CRS`
        object, or ``None`` if there isn't any.

        Raises an error if multiple CRS are found in the Dataset or DataArray."""
        if len(self.crs_indexes) == 0:
            return None
        elif len(self.crs_indexes) == 1:
            coord_name = next(iter(self.crs_indexes.keys()))
            return self.crs_indexes[coord_name].crs
        else:
            raise ValueError(
                f"Multiple CRS found: {list(self.crs_indexes.keys())}. "
                "Use .proj(coord_name).crs to select a specific one."
            )

    @property
    def crs_aware_indexes(self) -> Frozen[Hashable, xr.Index]:
        """Return an immutable dictionary of coordinate names as keys and
        xarray Index objects that are CRS-aware.

        A :term:`CRS-aware index` is an :py:class:`xarray.Index` object that
        must at least implements a method like
        :py:meth:`~xproj.ProjIndexMixin._proj_get_crs`."""
        if self._crs_aware_indexes_cache is None:
            self._cache_all_crs_indexes()
        return self._crs_aware_indexes_cache

    @property
    def crs_indexes(self) -> Frozen[Hashable, CRSIndex]:
        """Return an immutable dictionary of coordinate names as keys and
        :py:class:`~xproj.CRSIndex` objects as values.

        Return an empty dictionary if no coordinate with a CRSIndex is found."""
        if self._crs_indexes_cache is None:
            self._cache_all_crs_indexes()
        return self._crs_indexes_cache

    def map_crs(
        self,
        spatial_ref_coords: Any = None,
        allow_override: Any = False,
        transform: Any = False,
        **spatial_ref_coords_kwargs: Any,
    ) -> xr.DataArray | xr.Dataset:
        """Map spatial reference coordinate(s) to other indexed coordinates.

        This has an effect only if the latter coordinates have a
        :term:`CRS-aware index`. The index must then support setting the CRS via
        the :term:`proj index interface`.

        Parameters
        
        spatial_ref_coords : dict, optional
            A dict where the keys are the names of (scalar) spatial reference
            coordinates and values are the names of other coordinates with an index.
        allow_override : bool, optional
            If True, replace the CRS of the target index(es) even if they already have
            a CRS defined (default: False).
        transform : bool, optional
            If True (default: False), transform coordinate data to conform to the new CRS.
        **spatial_ref_coords_kwargs : optional
            The keyword arguments form of ``spatial_ref_coords``.
            One of ``spatial_ref_coords`` or ``spatial_ref_coords_kwargs`` must be provided.

        Returns
        
        Dataset or DataArray
            A new Dataset or DatArray object with updated CRS-aware indexes (and possibly
            updated coordinate data).
        """
        spatial_ref_coords = either_dict_or_kwargs(
            spatial_ref_coords, spatial_ref_coords_kwargs, "map_crs"
        )
        
        obj = self._obj
        for spatial_ref, target_coord in spatial_ref_coords.items():
            if spatial_ref not in self.crs_indexes:
                raise ValueError(f"Spatial reference coordinate '{spatial_ref}' not found or has no CRSIndex")
            
            if target_coord not in obj.xindexes:
                raise ValueError(f"Target coordinate '{target_coord}' has no index")
            
            target_index = obj.xindexes[target_coord]
            if not is_crs_aware(target_index):
                raise ValueError(f"Target coordinate '{target_coord}' is not CRS-aware")
            
            crs = self.crs_indexes[spatial_ref].crs
            
            if hasattr(target_index, "_proj_get_crs") and target_index._proj_get_crs() is not None and not allow_override:
                raise ValueError(
                    f"Target coordinate '{target_coord}' already has a CRS. "
                    "Use allow_override=True to replace it."
                )
            
            if transform and hasattr(target_index, "_proj_to_crs"):
                new_index = target_index._proj_to_crs(spatial_ref, crs)
            elif hasattr(target_index, "_proj_set_crs"):
                new_index = target_index._proj_set_crs(spatial_ref, crs)
            else:
                warnings.warn(
                    f"Target coordinate '{target_coord}' is CRS-aware but doesn't support setting CRS"
                )
                continue
            
            obj = obj.set_xindex(target_coord, new_index)
        
        return obj

    def write_crs_info(
        self, spatial_ref: Any = None, func: Any = format_compact_cf
    ) -> xr.DataArray | xr.Dataset:
        """Write CRS information as attributes to one or all spatial
        reference coordinates.

        Parameters
        
        spatial_ref : Hashable, optional
            The name of a :term:`spatial reference coordinate`. If not provided (default),
            CRS information will be written to all spatial reference coordinates found in
            the Dataset or DataArray. Each spatial reference coordinate must already have
            a :py:class:`~xproj.CRSIndex` associated.
        func : callable, optional
            Any callable used to format CRS information as coordinate variable attributes.
            The default function adds a ``crs_wkt`` attribute for compatibility with
            CF conventions.

        Returns
        
        Dataset or DataArray
            A new Dataset or DatArray object with attributes updated for one or all
            spatial reference coordinates.

        See Also
        
        ~xproj.format_compact_cf
        ~xproj.format_full_cf_gdal
        Dataset.proj.clear_crs_info
        DataArray.proj.clear_crs_info
        """
        return self._update_crs_info(spatial_ref, func)