from math import *
from numba import jit

'''
The `reckon` and `azimuth` functions are taken
from `AptDecoder.ji` and ported to Python3.
'''

@jit(nopython=True)
def azimuth(lat1, lon1, lat2, lon2):
    '''
    az = azimuth(lat1, lon1, lat2, lon2)

    Compute azimuth, i.e. the angle between the line segment
    defined by the points (`lat1`, `lon1`) and (`lat2`, `lon2`)
    and north.
    The units of all input and output parameters are degrees.
    See: https://en.wikipedia.org/wiki/Azimuth#Calculating_azimuth
    '''
    alpha_delta = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    alpha = atan(sin(alpha_delta) / (cos(lat1)*tan(lat2) - sin(lat1)*cos(alpha_delta)))

    return degrees(alpha)

@jit(nopython=True)
def reckon(lat, lon, range, azimuth):
    '''
    lato, lono = reckon(lat, lon, range, azimuth)

    Compute the coordinates of the end-point of a displacement on
    a sphere. `lat` and `lon` are the coordinates of the starting
    point, `range` is the covered distance of the displacements
    along a great circle and `azimuth` is the direction of the
    displacement relative to north.
    The units of all input and output parameters are degrees.
    '''
    lat = radians(lat)
    lon = radians(lon)
    range = radians(range)
    azimuth = radians(azimuth)

    tmp = sin(lat)*cos(range) + cos(lat)*sin(range)*cos(azimuth)

    # Clamp tmp between -1 and 1
    tmp = max(min(tmp, 1), -1)

    lato = pi/2 - acos(tmp)

    cos_gamma = (cos(range) - sin(lato)*sin(lat))/(cos(lato)*cos(lat))
    sin_gamma = sin(azimuth)*sin(range)/cos(lato)
    gamma = atan(sin_gamma / cos_gamma)

    lono = lon + gamma

    # Put lono in the interval (-pi -> pi)
    lono = (lono + pi) % (2*pi) - pi

    # Convert to degrees
    lono = degrees(lono)
    lato = degrees(lato)
    return (lato, lono)
