import pytest

import numpy as np

import scedar.eda as eda


class TestMultinomialMdl(object):
    """docstring for TestMultinomialMdl"""

    def test_empty_x(self):
        mmdl = eda.MultinomialMdl([])
        assert mmdl.mdl == 0

    def test_single_level(self):
        mmdl = eda.MultinomialMdl(["a"]*10)
        np.testing.assert_allclose(mmdl.mdl, np.log(10))

    def test_multi_levels(self):
        x = ["a"]*10 + ["b"]*25
        ux, uxcnt = np.unique(x, return_counts=True)
        mmdl = eda.MultinomialMdl(x)
        np.testing.assert_allclose(mmdl.mdl,
                                   (-np.log(uxcnt / len(x)) * uxcnt).sum())

    def test_wrong_x_shape(self):
        with pytest.raises(ValueError) as excinfo:
            eda.MultinomialMdl(np.arange(6).reshape(3, 2))

    def test_getter(self):
        mmdl = eda.MultinomialMdl([])
        assert mmdl.x == []
        mmdl2 = eda.MultinomialMdl([0, 0, 1, 1, 1])
        assert mmdl2.x == [0, 0, 1, 1, 1]


class TestZeroIdcGKdeMdl(object):
    """docstring for TestZeroIdcGKdeMdl"""
    x = np.concatenate([np.repeat(0, 50),
                        np.random.uniform(1, 2, size=200),
                        np.repeat(0, 50)])
    x_all_zero = np.repeat(0, 100)
    x_one_nonzero = np.array([0]*99 + [1])
    x_all_non_zero = x[50:250]

    def test_std_usage(self):
        zikm = eda.ZeroIdcGKdeMdl(self.x)
        np.testing.assert_allclose(zikm.x, self.x)

        assert zikm.x is not self.x
        np.testing.assert_allclose(zikm.x_nonzero, self.x[50:250])

        np.testing.assert_allclose(zikm.mdl, zikm.zi_mdl + zikm.kde_mdl)

        np.testing.assert_allclose(zikm.zi_mdl,
                                   np.log(3) + eda.MultinomialMdl(self.x != 0).mdl)

        assert zikm._bw_method == "silverman"

        assert zikm.bandwidth is not None

        # test > 0 value kde same
        zikm2 = eda.ZeroIdcGKdeMdl(self.x[50:250])
        np.testing.assert_allclose(zikm2.kde_mdl, zikm.kde_mdl)
        np.testing.assert_allclose(zikm2.bandwidth, zikm.bandwidth)

    def test_all_zero(self):
        zikm = eda.ZeroIdcGKdeMdl(self.x_all_zero)
        assert zikm.bandwidth is None
        np.testing.assert_allclose(zikm.zi_mdl, np.log(3))
        assert zikm.x_nonzero.size == 0
        np.testing.assert_allclose(zikm.x, self.x_all_zero)
        np.testing.assert_allclose(zikm.kde_mdl, 0)
        np.testing.assert_allclose(zikm.mdl, zikm.zi_mdl + zikm.kde_mdl)

    def test_all_nonzero(self):
        zikm = eda.ZeroIdcGKdeMdl(self.x_all_non_zero)
        np.testing.assert_allclose(zikm.zi_mdl, np.log(3))

    def test_one_nonzero(self):
        zikm = eda.ZeroIdcGKdeMdl(self.x_one_nonzero)
        assert zikm.bandwidth is None
        np.testing.assert_allclose(zikm.kde_mdl, np.log(1))

    def test_empty(self):
        zikm = eda.ZeroIdcGKdeMdl(np.array([]))
        assert zikm.mdl == 0
        assert zikm.zi_mdl == 0
        assert zikm.kde_mdl == 0

    def test_kde_bw(self):
        zikm = eda.ZeroIdcGKdeMdl(self.x)
        zikm2 = eda.ZeroIdcGKdeMdl(self.x, "scott")
        zikm3 = eda.ZeroIdcGKdeMdl(self.x, 1)
        xnz_std = zikm.x_nonzero.std(ddof=1)
        np.testing.assert_allclose(1, zikm3.bandwidth / xnz_std)
        assert not np.allclose(zikm2.bandwidth, zikm3.bandwidth)

    def test_wrong_x_shape(self):
        with pytest.raises(ValueError) as excinfo:
            eda.ZeroIdcGKdeMdl(np.arange(10).reshape(5, 2))

class TestGKdeMdl(object):
    """docstring for TestKdeMdl"""
    def test_wrong_x_shape(self):
        with pytest.raises(ValueError) as excinfo:
            eda.GKdeMdl(np.arange(10).reshape(5, 2))

    def test_x(self):
        gkmdl = eda.GKdeMdl(np.arange(100))
        np.testing.assert_equal(gkmdl.x, np.arange(100))
    
    def test_2d_kde(self):
        logdens = eda.GKdeMdl.gaussian_kde_logdens(
            np.random.normal(size=50).reshape(10, 5))
        assert logdens.ndim == 1
        assert logdens.size == 10

    def test_wrong_kde_x_shape(self):
        with pytest.raises(ValueError) as excinfo:
            eda.GKdeMdl.gaussian_kde_logdens(
                np.reshape(np.arange(9), (3, 3, 1)))
