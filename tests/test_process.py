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


def test_load_mesh_grib2(tmp_path):
    import eccodes

    path = tmp_path / 'test.grib2'
    gid = eccodes.codes_new_from_samples('GRIB2', eccodes.CODES_PRODUCT_GRIB)
    eccodes.codes_set(gid, 'Ni', 1)
    eccodes.codes_set(gid, 'Nj', 1)
    eccodes.codes_set(gid, 'latitudeOfFirstGridPointInDegrees', 0)
    eccodes.codes_set(gid, 'longitudeOfFirstGridPointInDegrees', 0)
    eccodes.codes_set(gid, 'latitudeOfLastGridPointInDegrees', 0)
    eccodes.codes_set(gid, 'longitudeOfLastGridPointInDegrees', 0)
    eccodes.codes_set(gid, 'iDirectionIncrementInDegrees', 1)
    eccodes.codes_set(gid, 'jDirectionIncrementInDegrees', 1)
    eccodes.codes_set_values(gid, [5])
    with open(path, 'wb') as f:
        eccodes.codes_write(gid, f)
    eccodes.codes_release(gid)

    lats, lons, data = load_mesh(str(path))
    assert lats.size == 1
    assert lons.size == 1
    assert data.shape == (1, 1)
