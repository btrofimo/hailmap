import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from process_mesh import load_mesh


def test_load_mesh(tmp_path):
    # create a small dummy netCDF file
    import netCDF4

    path = tmp_path / 'test.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('x', 2)
        ds.createDimension('y', 2)
        v = ds.createVariable('MESH', 'f4', ('y', 'x'))
        lat = ds.createVariable('lat', 'f4', ('y',))
        lon = ds.createVariable('lon', 'f4', ('x',))
        v[:] = np.array([[1, 2], [3, 4]])
        lat[:] = [0, 1]
        lon[:] = [0, 1]
    lats, lons, data = load_mesh(str(path))
    assert lats.shape == (2,)
    assert lons.shape == (2,)
    assert data.shape == (2, 2)
