# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring,too-many-arguments
import time

import numba
import numpy as np
import pytest
from mpi4py.MPI import ANY_SOURCE, ANY_TAG, COMM_WORLD

import numba_mpi as mpi
from tests.common import MPI_SUCCESS, data_types
from tests.utils import get_random_array

TEST_WAIT_FULL_IN_SECONDS = 0.3
TEST_WAIT_INCREMENT_IN_SECONDS = 0.1


@numba.njit
def jit_isend(data, dest, tag=0):
    return mpi.isend(data, dest, tag)


@numba.njit
def jit_irecv(data, source=ANY_SOURCE, tag=ANY_TAG):
    return mpi.irecv(data, source, tag)


@numba.njit
def jit_wait(request):
    return mpi.wait(request)


@numba.njit
def jit_test(request):
    return mpi.test(request)


@numba.njit
def jit_waitall(requests):
    return mpi.waitall(requests)


@pytest.mark.parametrize(
    "isnd, ircv, wait",
    (
        (jit_isend.py_func, jit_irecv.py_func, jit_wait.py_func),
        (jit_isend, jit_irecv, jit_wait),
    ),
)
@pytest.mark.parametrize("data_type", data_types)
def test_isend_irecv(isnd, ircv, wait, data_type):
    src = get_random_array((3, 3), data_type)
    dst_exp = np.empty_like(src)
    dst_tst = np.empty_like(src)

    if mpi.rank() == 0:
        status, req = isnd(src, dest=1, tag=11)
        assert status == MPI_SUCCESS

        req_exp = COMM_WORLD.Isend(src, dest=1, tag=22)

        status = wait(req)
        assert status == MPI_SUCCESS

        req_exp.wait()

    elif mpi.rank() == 1:
        status, req = ircv(dst_tst, source=0, tag=11)
        assert status == MPI_SUCCESS

        req_exp = COMM_WORLD.Irecv(dst_exp, source=0, tag=22)

        status = wait(req)
        assert status == MPI_SUCCESS

        req_exp.wait()

        np.testing.assert_equal(dst_tst, src)
        np.testing.assert_equal(dst_exp, src)


@pytest.mark.parametrize(
    "isnd, ircv, wait",
    (
        (jit_isend.py_func, jit_irecv.py_func, jit_wait.py_func),
        (jit_isend, jit_irecv, jit_wait),
    ),
)
def test_send_default_tag(isnd, ircv, wait):
    src = get_random_array(())
    dst_tst = np.empty_like(src)

    if mpi.rank() == 0:
        status, req = isnd(src, dest=1)
        assert status == MPI_SUCCESS
        wait(req)
    elif mpi.rank() == 1:
        status, req = ircv(dst_tst, source=0, tag=0)
        assert status == MPI_SUCCESS
        wait(req)

        np.testing.assert_equal(dst_tst, src)


@pytest.mark.parametrize(
    "isnd, ircv, wait",
    (
        (jit_isend.py_func, jit_irecv.py_func, jit_wait.py_func),
        (jit_isend, jit_irecv, jit_wait),
    ),
)
def test_recv_default_tag(isnd, ircv, wait):
    src = get_random_array(())
    dst_tst = np.empty_like(src)

    if mpi.rank() == 0:
        status, req = isnd(src, dest=1, tag=44)
        assert status == MPI_SUCCESS
        wait(req)
    elif mpi.rank() == 1:
        status, req = ircv(dst_tst, source=0)
        assert status == MPI_SUCCESS
        wait(req)

        np.testing.assert_equal(dst_tst, src)


@pytest.mark.parametrize(
    "isnd, ircv, wait",
    (
        (jit_isend.py_func, jit_irecv.py_func, jit_wait.py_func),
        (jit_isend, jit_irecv, jit_wait),
    ),
)
def test_recv_default_source(isnd, ircv, wait):
    src = get_random_array(())
    dst_tst = np.empty_like(src)

    if mpi.rank() == 0:
        status, req = isnd(src, dest=1, tag=44)
        assert status == MPI_SUCCESS
        wait(req)
    elif mpi.rank() == 1:
        status, req = ircv(dst_tst, tag=44)
        assert status == MPI_SUCCESS
        wait(req)

        np.testing.assert_equal(dst_tst, src)


@pytest.mark.parametrize(
    "isnd, ircv, tst, wait",
    [
        (jit_isend, jit_irecv, jit_test, jit_wait),
        (jit_isend.py_func, jit_irecv.py_func, jit_test.py_func, jit_wait.py_func),
    ],
)
def test_isend_irecv_test(isnd, ircv, tst, wait):
    src = get_random_array((5,))
    dst = np.empty_like(src)

    if mpi.rank() == 0:
        time.sleep(TEST_WAIT_FULL_IN_SECONDS)
        status, req = isnd(src, dest=1, tag=11)
        assert status == MPI_SUCCESS
        wait(req)
    elif mpi.rank() == 1:
        status, req = ircv(dst, source=0, tag=11)
        assert status == MPI_SUCCESS

        status, flag = tst(req)
        while status == MPI_SUCCESS and not flag:
            time.sleep(TEST_WAIT_INCREMENT_IN_SECONDS)
            status, flag = tst(req)

        np.testing.assert_equal(dst, src)
        wait(req)
