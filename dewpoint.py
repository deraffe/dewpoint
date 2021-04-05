#!/usr/bin/env python3

import argparse
import math

# Magnus parameters between -45°C and 60°C
alpha = 6.112  # hPA
beta = 17.62
gamma = 243.12  # °C


def saturation_vapour_pressure(temperature: float) -> float:
    return alpha * math.pow(
        math.e, (beta * temperature) / (gamma + temperature)
    )


def vapour_pressure(temperature: float, relative_humidity: float) -> float:
    return relative_humidity * saturation_vapour_pressure(temperature) / 100


def dewpoint(temperature: float, relative_humidity: float) -> float:
    vp_over_alpha = vapour_pressure(temperature, relative_humidity) / alpha
    dp1 = (gamma * math.log(vp_over_alpha)) / (beta - math.log(vp_over_alpha))
    dp_first_part = gamma * (
        math.log(relative_humidity / 100) + ((beta * temperature) /
                                             (gamma + temperature))
    )
    dp_second_part = beta - (
        math.log(relative_humidity / 100) + ((beta * temperature) /
                                             (gamma + temperature))
    )
    dp = dp_first_part / dp_second_part

    assert round(dp1, 10) == round(dp, 10), f'{dp1=} != {dp=}'
    return dp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'temperature', type=float, help='temperature in degrees celsius'
    )
    parser.add_argument(
        'relative_humidity', type=float, help='relative humidity in percent'
    )
    args = parser.parse_args()
    t = args.temperature
    rh = args.relative_humidity
    dp = dewpoint(t, rh)
    print(f'The dewpoint at {t}°C and {rh}% rel. humidity is {dp}°C')


if __name__ == '__main__':
    main()
