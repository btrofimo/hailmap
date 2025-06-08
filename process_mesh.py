import gzip
import os
from typing import Tuple
import numpy as np
from netCDF4 import Dataset


def _open_dataset(path: str) -> Dataset:
    """Open a netCDF dataset, handling optional gzip compression."""
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
    # Try common variable names
    var_candidates = ['MESH', 'MaxEstimatedHailSize', 'value']
    var = None
    for name in var_candidates:
        if name in ds.variables:
            var = ds.variables[name]
            break
    if var is None:
        # fallback: first variable
        var = next(iter(ds.variables.values()))
    data = np.array(var[:])
    lats = np.array(ds.variables.get('Latitude', ds.variables.get('lat'))[:])
    lons = np.array(ds.variables.get('Longitude', ds.variables.get('lon'))[:])
    ds.close()
    return lats, lons, data
