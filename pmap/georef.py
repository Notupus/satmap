from math import *
import datetime as dt
from orbit_predictor import coordinate_systems
from numba import jit
import cv2
import numpy as np
from scipy.interpolate import interp1d

from pmap.config import earth_radius, segment_size
from pmap.geomap import azimuth, reckon

@jit(nopython=True)
def map_clamp(x, in_min, in_max, out_min, out_max):
    '''
    x = map(x, in_min, in_max, out_min, out_max)

    Map `x` in the range [`in_min`, `in_max`] to the range
    [`out_min`, `out_max`] and clamp it to the boundaries.
    '''
    x = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if(x >= out_max):
        return out_max
    if(x <= out_min):
        return out_min
    return x

@jit(nopython=True)
def map_value(x, in_min, in_max, out_min, out_max):
    '''
    x = map(x, in_min, in_max, out_min, out_max)

    Map `x` in the range [`in_min`, `in_max`] to the range
    [`out_min`, `out_max`].
    '''
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

@jit(nopython=True)
def latlon2px(lat, lon, width, height):
    '''
    Converts a lat/lon value to a point on a Mercator map.
    Returns a tuple of (x, y).
    '''
    return (
        (lon/180)*(width/2)+(width/2),
        (-lat/90)*(height/2)+(height/2),
    )

def interp_zeros(arr):
    '''
    Replace zeros in an array the interpolated values between
    the two extremes.
    TODO: this is bad, and not very pythonic
    '''
    for i in range(0, len(arr)-1):
        elements = np.nonzero(arr[i])
        if len(elements[0]):
            start = elements[0][0]
            end = elements[0][-1]

            y = arr[i][start:end]
            y[0] = 1; y[-1] = 1

            x = np.arange(len(y))
            idx = np.nonzero(y)
            interp = interp1d(x[idx], y[idx])
            arr[i][start:end] = interp(x)
    
    return arr

def propergate_orbit(predictor, time, lines_per_second, rows):
    '''
    orbit = propergate_orbit(predictor, time, lines_per_second, rows)

    Calculate the satellite prediction for each row of an image, where
    `rows` is the number of rows to calculate, `time` is the calculation
    start time and `predictor` is a orbit_predictor source.
    '''
    orbit = []
    for i in range(0, rows):
        orbit.append(coordinate_systems.ecef_to_llh(predictor.get_only_position(time)))
        time += dt.timedelta(seconds=1/lines_per_second)
    return orbit

def map_image(image_file, output_file, output_size, extent, swath_size, predictor, time, lines_per_second):
    '''
    Sat image -> Mercator version of the image
    '''
    # Source image
    src = cv2.imread(image_file)
    src_height, src_width = src.shape[:2]

    # Deform mesh (for OpenCV)
    xs, ys = np.meshgrid(np.zeros(output_size[0]), np.zeros(output_size[1]))
    xs = xs.astype(np.float32)
    ys = ys.astype(np.float32)

    # Calculate swath angle
    swath = swath_size / radians(earth_radius)

    # Calculate the satellite orbit over the course of the image
    orbit = propergate_orbit(predictor, time, lines_per_second, src_height)

    # Warp the image
    for y in range(1, src_height-1):
        # Perpendicular angle of satellite path at this point
        angle = azimuth(orbit[y-1][0], orbit[y-1][1], orbit[y+1][0], orbit[y+1][1]) + 90

        # Positions of segment edge in this row
        range_angle = -swath/2
        for x in range(0, src_width):
            # Latitude and longitude of this pixel
            lat, lon = reckon(orbit[y][0], orbit[y][1], range_angle, angle)
            
            mapx = round(map_clamp(lon, extent[0], extent[1], 0, output_size[0]-1))
            mapy = round(map_clamp(lat, extent[3], extent[2], 0, output_size[1]-1))
            ys[mapy, mapx] = y
            xs[mapy, mapx] = x

            range_angle += swath/src_width

    # Post process and write image
    ys = interp_zeros(ys)
    xs = interp_zeros(xs)
    dest = cv2.remap(src, xs, ys, cv2.INTER_CUBIC)
    cv2.imwrite(output_file, dest)

def create_underlay(size, output_file, swath_size, predictor, time, lines_per_second, map_filename):
    '''
    Make a map for a image
    '''
    src_width, src_height = size

    # Map image
    src = cv2.imread(map_filename)
    map_height, map_width = src.shape[:2]

    # Deform mesh (for OpenCV)
    xs, ys = np.meshgrid(np.zeros(src_width), np.zeros(src_height))
    xs = xs.astype(np.float32)
    ys = ys.astype(np.float32)

    # Calculate angle of swath
    swath = swath_size / radians(earth_radius)

    orbit = propergate_orbit(predictor, time, lines_per_second, src_height)
    for y in range(1, src_height-1):
        # Perpendicular angle of path
        angle = azimuth(orbit[y-1][0], orbit[y-1][1], orbit[y+1][0], orbit[y+1][1]) + 90

        range_angle = -swath/2
        for x in range(0, src_width):
            # Latitude and longitude of this pixel
            lat, lon = reckon(orbit[y][0], orbit[y][1], range_angle, angle)

            xs[y, x], ys[y, x] = latlon2px(lat, lon, map_width, map_height)

            range_angle += swath/src_width

    # Write image
    dest = cv2.remap(src, xs, ys, cv2.INTER_CUBIC)
    cv2.imwrite(output_file, dest)