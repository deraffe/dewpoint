#!/usr/bin/env python3
"""Calculate the wet-bulb temperature for a given temperature and relative humidity.

Based on information from [0] / [1].

0. https://www.mit.edu/~eltahirgroup/calTW.html
1. Davies-Jones, R. (2008).
   "An Efficient and Accurate Method for Computing the Wet-Bulb Temperature
   along Pseudoadiabats."
   Monthly Weather Review, 136(7), 2764-2785.
   https://doi.org/10.1175/2007MWR2224.1
"""

import logging
import math

log = logging.getLogger(__name__)

Kelvin = float
Celsius = float
Percent = float
Millibar = float

TEMP_ZEROCELSIUS: Kelvin = 273.15
# Poisson constant for dry air
# K_d = R_d / c_pd
# Source: https://glossarystaging.ametsoc.net/wiki/Poisson_constant
POISSON_DRY_AIR = 0.2854


def kelvin2celsius(temperature: Kelvin) -> Celsius:
    return temperature - TEMP_ZEROCELSIUS


def celsius2kelvin(temperature: Celsius) -> Kelvin:
    return temperature + TEMP_ZEROCELSIUS


def wetbulb_temperature(temperature: Celsius, relative_humidity: Percent) -> Celsius:
    temperature_kelvin = celsius2kelvin(temperature)
    temperature_dewpoint_kelvin = dewpoint_temperature_kelvin(
        relative_humidity, temperature_kelvin
    )
    return wetbulb_temperature_celsius(
        temperature_kelvin, temperature_dewpoint_kelvin, 101300
    )


def dewpoint_temperature_kelvin(
    relative_humidity: Percent, temperature_kelvin: Kelvin
) -> Kelvin:
    GC = 461.5
    GCX = GC / (1000.0 * 4.186)

    LHV = (597.3 - 0.57 * (temperature_kelvin - 273.0)) / GCX
    TDK = (
        temperature_kelvin
        * LHV
        / (LHV - temperature_kelvin * math.log(relative_humidity * 0.01))
    )

    return TDK


def wetbulb_temperature_celsius(
    temp_drybulb: Kelvin, temp_dewpoint: Kelvin, ps
) -> Celsius:
    svp1: Millibar = 6.112  # e_s(C)
    svp2 = 17.67  # a
    svp3 = 29.65
    svp4: Kelvin = 243.5  # b
    ep2 = 0.622  # epsilon
    big_a_k: Kelvin = 2675.0  # A
    po: Millibar = 1000.0
    # lam is about 3.504  # lambda = 1/K_d
    lam = 1 / POISSON_DRY_AIR

    tempc_drybulb = kelvin2celsius(temp_drybulb)

    tempc_dewpoint = kelvin2celsius(temp_dewpoint)

    p = ps / 100.0

    U = math.exp((svp2 * (tempc_dewpoint)) / (svp4 + tempc_dewpoint)) / math.exp(
        (svp2 * tempc_drybulb) / (tempc_drybulb + svp4)
    )

    if temp_drybulb > TEMP_ZEROCELSIUS:
        es = svp1 * math.exp(svp2 * tempc_drybulb / (tempc_drybulb + svp4))
    else:
        es = svp1 * math.exp(22.514 - 6.15e3 / temp_drybulb)

    e = U * es

    temp_lifted_condensation_level = (
        1.0
        / (
            1.0 / (temp_dewpoint - 56.0)
            + math.log(temp_drybulb / temp_dewpoint) / 800.0
        )
        + 56.0
    )  # Temperature at LCL (K) → theta_W
    r = ep2 * e / (p - e)

    temp_potential_lifted_condensation_level = (
        temp_drybulb
        * ((po / (p - e)) ** POISSON_DRY_AIR)
        * (temp_drybulb / temp_lifted_condensation_level) ** (0.28 * r)
    )  # Potential (dry) temperature at LCL (K)
    temp_equivalent_potential = temp_potential_lifted_condensation_level * math.exp(
        (3036.0 / temp_lifted_condensation_level - 1.78) * r * (1.0 + 0.448 * r)
    )  # Equivalent potential temperature (K)

    pressure_nondimensional = (p / po) ** (
        1.0 / lam
    )  # bottom left of pg 2766 → pi = (p/p_0)**(1/lambda)
    TE = temp_equivalent_potential * pressure_nondimensional

    if TE > TEMP_ZEROCELSIUS:
        es_te = svp1 * math.exp(svp2 * (TE - TEMP_ZEROCELSIUS) / (TE - svp3))
    else:
        es_te = svp1 * math.exp(22.514 - 6.15e3 / TE)

    rs_te = ep2 * es_te / (p - es_te)  # Saturation mixing ratio at TE (kg/kg)

    k1_pi = (
        -38.5 * pressure_nondimensional**2 + 137.81 * pressure_nondimensional - 53.737
    )  # eqn 4.3
    k2_pi = (
        -4.392 * pressure_nondimensional**2 + 56.831 * pressure_nondimensional - 0.384
    )  # eqn 4.4

    cote = (TEMP_ZEROCELSIUS / TE) ** lam
    D_pi = 1.0 / (0.1859 * pressure_nondimensional / po + 0.6512)  # D(pi) eqn 4.7

    if cote > D_pi:
        d_este = svp2 * svp4 / (TE - TEMP_ZEROCELSIUS + svp4) ^ 2  # below eqn 3.7
        tempc_wetbulb = (
            TE - TEMP_ZEROCELSIUS - big_a_k * rs_te / (1.0 + big_a_k * rs_te * d_este)
        )  # eqn 4.8
    elif cote >= 1.0 and cote <= D_pi:
        tempc_wetbulb = k1_pi - k2_pi * cote  # eqn 4.9
    elif cote >= 0.4 and cote < 1.0:
        tempc_wetbulb = (k1_pi - 1.21) - (k2_pi - 1.21) * cote  # eqn 4.10
    elif cote < 0.4:
        tempc_wetbulb = (k1_pi - 2.66) - (k2_pi - 1.21) * cote + 0.58 / cote  # eqn 4.11

    return tempc_wetbulb
