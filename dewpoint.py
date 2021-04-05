#!/usr/bin/env python3

import argparse
import logging
import math

log = logging.getLogger(__name__)

# Magnus parameters between -45°C and 60°C
alpha = 6.112  # hPA
beta = 17.62
gamma = 243.12  # °C


def saturation_vapour_pressure(temperature: float) -> float:
    svp = alpha * math.pow(
        math.e, (beta * temperature) / (gamma + temperature)
    )
    log.debug(f'saturation vapour pressure at {temperature}°C: {svp:.2f}hPA')
    return svp


def vapour_pressure(temperature: float, relative_humidity: float) -> float:
    vp = relative_humidity * saturation_vapour_pressure(temperature) / 100
    log.debug(
        f'vapour pressure at {temperature}°C and {relative_humidity}%RH: {vp:.2f}hPA'
    )
    return vp


def dewpoint_1(temperature: float, relative_humidity: float) -> float:
    vp_over_alpha = vapour_pressure(temperature, relative_humidity) / alpha
    dp1 = (gamma * math.log(vp_over_alpha)) / (beta - math.log(vp_over_alpha))
    log.debug(f'{dp1=}°C')
    return dp1


def dewpoint_2(temperature: float, relative_humidity: float) -> float:
    dp_zeroeth_part = math.log(relative_humidity / 100
                               ) + ((beta * temperature) /
                                    (gamma + temperature))
    dp_first_part = gamma * dp_zeroeth_part
    dp_second_part = beta - dp_zeroeth_part
    dp = dp_first_part / dp_second_part

    return dp


def dewpoint_3(t: float, rh: float) -> float:
    H = (math.log10(rh) - 2) / 0.4343 + (17.62 * t) / (243.12 + t)
    dp = 243.12 * H / (17.62 - H)
    return dp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'temperature', type=float, help='temperature in degrees celsius'
    )
    parser.add_argument(
        'relative_humidity', type=float, help='relative humidity in percent'
    )
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)

    t = args.temperature
    rh = args.relative_humidity
    dp1 = dewpoint_1(t, rh)
    dp2 = dewpoint_2(t, rh)
    dp3 = dewpoint_3(t, rh)
    precision = 4
    assert round(dp1, precision) == round(dp2, precision) == round(
        dp3, precision
    ), f'{dp1=} != {dp2=} != {dp3=}'
    print(f'The dewpoint at {t}°C and {rh}% rel. humidity is {dp:.2f}°C')


if __name__ == '__main__':
    main()
