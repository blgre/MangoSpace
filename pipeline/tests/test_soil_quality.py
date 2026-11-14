import unittest

import numpy as np

from check_soil_quality import recommended


class QualityTest(unittest.TestCase):
    def test_algorithm_bits_do_not_reject_good_retrievals(self):
        valid, good = recommended(
            np.array([0.2, 0.3, 0.4, -9999, np.nan, 0.2]),
            np.array([0, 8, 9, 8, 0, -9999]), -9999, -9999,
        )
        np.testing.assert_array_equal(valid, [True, True, True, False, False, False])
        np.testing.assert_array_equal(good, [True, True, False, False, False, False])
