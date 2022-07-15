#!/usr/bin/env python3
"""Calculate the dewpoint for a given temperature and relative humidity and vice versa.

Based on information from Sensirion[0] and Bernd Kuemmel[1].

0. http://irtfweb.ifa.hawaii.edu/~tcs3/tcs3/Misc/Dewpoint_Calculation_Humidity_Sensor_E.pdf
1. http://www.faqs.org/faqs/meteorology/temp-dewpoint/
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


def dewpoint_all(t: float, rh: float) -> float:
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
    return dp1


def relative_humidity(t: float, td: float) -> float:
    rhd = saturation_vapour_pressure(td) / saturation_vapour_pressure(t)
    log.debug(f'{rhd=:%}')
    return rhd


def temperature(td: float, rh: float) -> float:
    rhd = rh / 100
    pst = saturation_vapour_pressure(td) / rhd
    log.debug(
        f'saturation vapour pressure for wanted temperature: {pst:.2f}hPA'
    )
    t = (lambda_ * math.log(pst / alpha)) / (beta - math.log(pst / alpha))
    log.debug(f'Temperature: {t:.2f}°C')
    return t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--temperature',
        type=float,
        help='temperature in degrees celsius'
    )
    parser.add_argument(
        '-r',
        '--relative_humidity',
        type=float,
        help='relative humidity in percent'
    )
    parser.add_argument(
        '-d', '--dew_point', type=float, help='dew point in degrees celcius'
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
    td = args.dew_point

    if t is not None:
        if not t_low < t < t_high:
            log.warning(
                f'Temperature {t}°C is outside of the bounds for which the used constants are defined. ({t_low}°C – {t_high}°C)'
            )

    if t is not None and rh is not None:
        log.info('Calculating dew point...')
        dp = dewpoint_all(t, rh)
        print(f'The dewpoint at {t}°C and {rh}% rel. humidity is {dp:.2f}°C')
    elif t is not None and td is not None:
        log.info('Calculating relative humidity...')
        rhd = relative_humidity(t, td)
        print(
            f'The relative humidity at {t}°C and {td}°C dewpoint is {rhd:.2%}'
        )
    elif rh is not None and td is not None:
        log.info('Calculating temperature...')
        t = temperature(td, rh)
        print(
            f'The temperature for dewpoint {td:.2f}°C and relative humidity of {rh}% is {t:.2f}°C'
        )
    else:
        log.fatal(
            'Provide at least two of temperature, relative humidity and dew point.'
        )


if __name__ == '__main__':
    main()
