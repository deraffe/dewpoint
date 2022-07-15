#!/usr/bin/env python3
"""Calculate the dewpoint for a give temperature and relative humidity.

Based on information from Sensirion[0].

0. http://irtfweb.ifa.hawaii.edu/~tcs3/tcs3/Misc/Dewpoint_Calculation_Humidity_Sensor_E.pdf
"""

import argparse
import logging
import math

log = logging.getLogger(__name__)

# Magnus parameters between -45°C and 60°C
alpha = 6.112  # hPA
beta = 17.62
lambda_ = 243.12  # °C
t_low = -45
t_high = 60


def saturation_vapour_pressure(temperature: float) -> float:
    svp = alpha * math.pow(
        math.e, (beta * temperature) / (lambda_ + temperature)
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
    dp1 = (lambda_ *
           math.log(vp_over_alpha)) / (beta - math.log(vp_over_alpha))
    log.debug(f'{dp1=}°C')
    return dp1


def dewpoint_2(temperature: float, relative_humidity: float) -> float:
    dp_zeroeth_part = math.log(relative_humidity / 100
                               ) + ((beta * temperature) /
                                    (lambda_ + temperature))
    dp_first_part = lambda_ * dp_zeroeth_part
    dp_second_part = beta - dp_zeroeth_part
    dp2 = dp_first_part / dp_second_part
    log.debug(f'{dp2=}°C')
    return dp2


def dewpoint_3(t: float, rh: float) -> float:
    H = (math.log10(rh) - 2) / 0.4343 + (beta * t) / (lambda_ + t)
    dp3 = lambda_ * H / (beta - H)
    log.debug(f'{dp3=}°C')
    return dp3


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
    if not t_low < t < t_high:
        log.warning(
            f'Temperature {t}°C is outside of the bounds for which the used constants are defined. ({t_low}°C – {t_high}°C)'
        )
    rh = args.relative_humidity
    dp1 = dewpoint_1(t, rh)
    dp2 = dewpoint_2(t, rh)
    dp3 = dewpoint_3(t, rh)
    deviation = dp3 - dp1
    log.debug(f'deviation of simple algo: {deviation}°C')
    allowed_difference = 0.001
    diff1 = abs(dp2 - dp1)
    log.debug(f'{diff1=}')
    diff2 = abs(dp3 - dp1)
    log.debug(f'{diff2=}')
    assert diff1 < diff2 < allowed_difference, f'{dp1=} !~ {dp2=} !~ {dp3=}'
    print(f'The dewpoint at {t}°C and {rh}% rel. humidity is {dp1:.2f}°C')


if __name__ == '__main__':
    main()
