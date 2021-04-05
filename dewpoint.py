#!/usr/bin/env python3

import argparse
import logging
import math

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()


if __name__ == '__main__':
    main()

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


def dewpoint(temperature: float, relative_humidity: float) -> float:
    vp_over_alpha = vapour_pressure(temperature, relative_humidity) / alpha
    dp1 = (gamma * math.log(vp_over_alpha)) / (beta - math.log(vp_over_alpha))
    log.debug(f'{dp1=}°C')
    dp_zeroeth_part = math.log(relative_humidity / 100
                               ) + ((beta * temperature) /
                                    (gamma + temperature))
    dp_first_part = gamma * dp_zeroeth_part
    dp_second_part = beta - dp_zeroeth_part
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
    dp = dewpoint(t, rh)
    print(f'The dewpoint at {t}°C and {rh}% rel. humidity is {dp:2.f}°C')


if __name__ == '__main__':
    main()
