import unittest

import numpy as np
import sigpy as sp

from pulpy.grad.trajgrad import spiral_k, stack_of
from pulpy.linop import PtxSpatialExplicit

if __name__ == "__main__":
    unittest.main()


def check_linop_adjoint(A, dtype=np.float32, device=sp.cpu_device):
    device = sp.Device(device)
    x = sp.randn(A.ishape, dtype=dtype, device=device)
    y = sp.randn(A.oshape, dtype=dtype, device=device)

    xp = device.xp
    with device:
        lhs = xp.vdot(A * x, y)
        rhs = xp.vdot(x, A.H * y)

        xp.testing.assert_allclose(lhs, rhs, atol=1e-5, rtol=1e-5)


class TestLinop(unittest.TestCase):
    def test_spatial_explicit_model(self):
        dim = 3
        img_shape = [dim, dim, dim]
        mps_shape = [8, dim, dim, dim]

        dt = 4e-6

        k = spiral_k(
            fov=dim / 2,
            N=dim,
            f_sampling=1,
            R=1,
            ninterleaves=1,
            alpha=1,
            gm=0.03,
            sm=200,
        )
        k = stack_of(k, 3, 0.1)

        mps = sp.randn(mps_shape, dtype=np.complex64)

        A = PtxSpatialExplicit(mps, k, dt, img_shape)

        check_linop_adjoint(A, dtype=np.complex64)
