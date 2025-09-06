from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    import pyproj
    import xarray as xr

T_Xarray_Object = TypeVar("T_Xarray_Object")


class ProjAccessorMixin:
    """Mixin class that marks XProj support for an Xarray accessor."""

    def _proj_set_crs(self, spatial_ref, crs):
        """Method called when setting a new CRS via
        :py:meth:`xarray.Dataset.proj.assign_crs()`.

        Parameters
        
        spatial_ref : Hashable
            The name of the spatial reference (scalar) coordinate
            to which the CRS has been set.
        crs : pyproj.crs.CRS
            The new CRS attached to the spatial reference coordinate.

        Returns
        
        xarray.Dataset or xarray.DataArray
            Either a new or an existing Dataset or DataArray.
        """
        return self._obj


class ProjIndexMixin:
    """Mixin class that marks XProj support for an Xarray index."""

    def _proj_get_crs(self):
        """XProj access to the CRS of the index.

        Returns
        
        pyproj.crs.CRS or None
            The CRS of the index or None if not (yet) defined.
        """
        return None

    def _proj_set_crs(self, spatial_ref, crs):
        """Method called when mapping a CRS to index coordinate(s) via
        :py:meth:`xarray.Dataset.proj.map_crs`.

        Parameters
        
        spatial_ref : Hashable
            The name of the spatial reference (scalar) coordinate.
        crs : pyproj.crs.CRS
            The new CRS attached to the spatial reference coordinate.

        Returns
        
        Index
            Either a new or an existing xarray Index.
        """
        return self

    def _proj_to_crs(self, spatial_ref, crs):
        """Method called when mapping a CRS to index coordinate(s) via
        :py:meth:`xarray.Dataset.proj.map_crs` with ``transform=True``.

        Parameters
        
        spatial_ref : Hashable
            The name of the spatial reference (scalar) coordinate.
        crs : pyproj.crs.CRS
            The new CRS attached to the spatial reference coordinate.

        Returns
        
        Index
            Either a new or an existing xarray Index.
        """
        return self