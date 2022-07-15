#!/usr/bin/env python

import unittest

from dewpoint import *


class DewpointApproximationTests(unittest.TestCase):
    known_good_values = (
        (25.14, 32, 7.335),  # measurement from DWD (slightly tweaked)
        (25, 10, -8.77),  # example from Sensirion
        (50, 90, 47.90),  # example from Sensirion
        (25, 50, 13.85),  # example from Bernd Kuemmel
    )

    def test_dewpoint_calculation(self):
        for t, r, d in self.known_good_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(dewpoint_all(t, r), d, delta=0.2)

    def test_relative_humidity_calculation(self):
        for t, r, d in self.known_good_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(
                    relative_humidity(t, d) * 100, r, delta=0.2
                )

    def test_temperature_calculation(self):
        for t, r, d in self.known_good_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(temperature(d, r), t, delta=0.2)


class DewpointLimitTests(unittest.TestCase):
    test_values = (
        (-260, 1, -260.3),
        (1, 0.1, -68),
        (-40, 0.101, -90),
        (100, 99, 99.7),
    )

    def test_dewpoint_calculation(self):
        for t, r, d in self.test_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(dewpoint_all(t, r), d, delta=0.2)

    def test_relative_humidity_calculation(self):
        for t, r, d in self.test_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(
                    relative_humidity(t, d) * 100, r, delta=0.2
                )

    def test_temperature_calculation(self):
        for t, r, d in self.test_values:
            with self.subTest(t=t, r=r, d=d):
                self.assertAlmostEqual(temperature(d, r), t, delta=0.2)


if __name__ == "__main__":
    unittest.main()
