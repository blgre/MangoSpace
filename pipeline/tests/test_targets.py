import unittest

import numpy as np

import targets

LAND, WATER = -7.0, -18.0
RESERVOIR = (slice(100, 200), slice(100, 300))
RESERVOIR_KM2 = round(20_000 * targets.PIXEL_KM2, 3)


def scene():
    hh = np.full((targets.SIZE, targets.SIZE), LAND)
    hh[RESERVOIR] = WATER
    return hh


class TargetImageTest(unittest.TestCase):
    def test_grey_scale_follows_the_data_contract(self):
        db = np.array([[-40.0, -30.0, -15.0, 0.0, 5.0, np.nan]])
        self.assertEqual(targets.to_grey(db).tolist(), [[0, 0, 128, 255, 255, 0]])

    def test_a_pixel_is_about_ten_metres(self):
        self.assertAlmostEqual(targets.PIXEL_KM2 * 1e6, 100, delta=1)

    def test_despeckle_takes_the_mean_power_and_not_the_mean_db(self):
        speckle = np.where(np.indices((20, 20)).sum(0) % 2, -20.0, 0.0)
        self.assertAlmostEqual(targets.despeckle(speckle)[10, 10], 10 * np.log10((13 * 1 + 12 * 0.01) / 25), places=3)


class WaterAreaTest(unittest.TestCase):
    def area(self, hh, others=2):
        return targets.water_area_km2(hh, targets.reservoir_outline([hh] + [scene()] * others))

    def test_counts_the_reservoir(self):
        self.assertEqual(self.area(scene()), RESERVOIR_KM2)

    def test_counts_water_that_wind_made_brighter(self):
        windy = scene()
        windy[RESERVOIR] = -14.0
        self.assertEqual(self.area(windy), RESERVOIR_KM2)

    def test_does_not_count_a_wet_field_outside_the_reservoir(self):
        planting = scene()
        planting[300:400, 100:300] = WATER
        self.assertEqual(self.area(planting), RESERVOIR_KM2)

    def test_area_falls_when_the_water_leaves_part_of_the_reservoir(self):
        dry = scene()
        dry[100:200, 100:200] = LAND
        self.assertEqual(self.area(dry), round(10_000 * targets.PIXEL_KM2, 3))


if __name__ == "__main__":
    unittest.main()
