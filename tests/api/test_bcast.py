# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring
import numba
import numpy as np
import pytest

import numba_mpi as mpi
from tests.common import data_types
from tests.utils import get_random_array


@numba.njit()
def jit_bcast(data, root):
    return mpi.bcast(data, root)


@pytest.mark.parametrize("bcast", (jit_bcast.py_func, jit_bcast))
@pytest.mark.parametrize("data_type", data_types)
@pytest.mark.parametrize("root", range(mpi.size()))
def test_bcast_np_array(data_type, bcast, root):
    data = np.empty(5, data_type).astype(dtype=data_type)
    datatobcast = get_random_array(5, data_type).astype(dtype=data_type)

    if mpi.rank() == root:
        data = datatobcast

    status = bcast(data, root)

    assert status == mpi.SUCCESS

    np.testing.assert_equal(data, datatobcast)


@pytest.mark.parametrize(
    "stringtobcast",
    ("test bcast", pytest.param("żółć", marks=pytest.mark.xfail(strict=True))),
)
@pytest.mark.parametrize("root", range(mpi.size()))
def test_bcast_string(stringtobcast, root):
    datatobcast = np.array(stringtobcast, "c")
    data = np.empty_like(datatobcast)

    if mpi.rank() == root:
        data = datatobcast

    status = mpi.bcast(data, root)
    assert status == mpi.SUCCESS
    assert str(data) == str(datatobcast)
