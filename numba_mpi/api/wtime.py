"""MPI_Wtime() implementation"""
import ctypes

import numba
import numpy as np

from numba_mpi.common import libmpi

_MPI_Wtime = libmpi.MPI_Get_wtime
_MPI_Wtime.restype = ctypes.c_double
_MPI_Wtime.argtypes = []

@numba.njit()
def wtime():
    """wrapper for MPI_Wtime()"""
    return _MPI_Wtime()
