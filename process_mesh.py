import gzip
import os
from typing import Tuple
import numpy as np
from netCDF4 import Dataset
import xarray as xr


def _open_dataset(path: str):
    """Open a hail dataset. Supports NetCDF and GRIB2."""
    if path.endswith('.grib2'):
        return xr.open_dataset(path, engine='cfgrib')

    if path.endswith('.gz'):
        tmp_path = path[:-3]
        with gzip.open(path, 'rb') as f_in, open(tmp_path, 'wb') as f_out:
            f_out.write(f_in.read())
        ds = Dataset(tmp_path)
        os.remove(tmp_path)
    else:
        ds = Dataset(path)
    return ds


def load_mesh(path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return lat, lon, mesh arrays from a MRMS MESH file."""
    ds = _open_dataset(path)

    var_candidates = ['MESH', 'MaxEstimatedHailSize', 'value']

    if path.endswith('.grib2'):
        var_name = None
        for name in var_candidates:
            if name in ds.data_vars:
                var_name = name
                break
        if var_name is None:
            var_name = list(ds.data_vars)[0]
        data = ds[var_name].values
        lat_obj = ds['latitude'] if 'latitude' in ds else ds.coords.get('lat')
        lon_obj = ds['longitude'] if 'longitude' in ds else ds.coords.get('lon')
        lats = np.array(lat_obj.values)
        lons = np.array(lon_obj.values)
        ds.close()
        return lats, lons, data

    # netCDF path
    var = None
    for name in var_candidates:
        if name in ds.variables:
            var = ds.variables[name]
            break
    if var is None:
        var = next(iter(ds.variables.values()))

    data = np.array(var[:])
    lats = np.array(ds.variables.get('Latitude', ds.variables.get('lat'))[:])
    lons = np.array(ds.variables.get('Longitude', ds.variables.get('lon'))[:])
    ds.close()
    return lats, lons, data
