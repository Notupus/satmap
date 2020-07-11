from math import *
import datetime as dt
from orbit_predictor import coordinate_systems
from numba import jit
import cv2
import numpy as np
import shapefile

from satmap.config import earth_radius, polar_radius, equtorial_radius
from satmap.geomap import azimuth, reckon

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

@jit(nopython=True)
def latlon2px(lat, lon, width, height):
    '''
    Converts a lat/lon value to a point on a Mercator map.
    Returns a tuple of (x, y).
    '''
    lon *= sin(radians(lat+90))
    return (
        (lon/180)*(width/2)+(width/2),
        (-lat/90)*(height/2)+(height/2)
    )

@jit(nopython=True)
def latlon2px_int(lat, lon, width, height):
    x, y = latlon2px(lat, lon, width, height)
    return (int(x), int(y))

def render_shapefile(filename, image, size):
    shp = shapefile.Reader(filename)
    for shape in shp.iterShapes():
        npoints = len(shape.points)
        nparts = len(shape.parts)

        for i in range(nparts):
            start = shape.parts[i]
            if i < nparts-1:
                end = shape.parts[i+1]-1
            else:
                end = npoints

            seg = shape.points[start:end+1]
            for j in range(1, len(seg)):
                # TODO: why the fuck does this function have no antialising
                # FIXME: use the polygron draw function here
                cv2.line(image,
                    latlon2px_int(seg[j-1][1], seg[j-1][0], size[0], size[1]),
                    latlon2px_int(seg[j][1],   seg[j][0],   size[0], size[1]),
                (255, 255, 40), thickness=2)

def make_map(predictor, sat_swath, sat_lps, width, height, time, outname):
    # Deform mesh (for OpenCV)
    xs, ys = np.meshgrid(np.zeros(width), np.zeros(height))
    xs = xs.astype(np.float32)
    ys = ys.astype(np.float32)

    # Calculate the satellite orbit over the course of the image
    orbit = propergate_orbit(predictor, time, sat_lps, height)

    # Render map (have to use massive oversampling here due to no fucking AA),
    # This isnt even the proper way of doing it anyway
    map_width = 20000
    map_height = 10000
    image = np.zeros((map_height, map_width, 3))
    render_shapefile("countries.shp", image, (map_width, map_height))

    for y in range(1, height-1):
        polar = abs(orbit[y][1])/90
        current_radius = polar_radius*polar + equtorial_radius*(1-polar)
        swath = sat_swath / radians(current_radius)
        skew = polar*7 - 3

        angle = azimuth(orbit[y-1][0], orbit[y-1][1], orbit[y+1][0], orbit[y+1][1]) + 90 + skew

        range_angle = -swath/2
        for x in range(width):
            lat, lon = reckon(orbit[y][0], orbit[y][1], range_angle, angle)
            xs[y, x], ys[y, x] = latlon2px(lat, lon, map_width, map_height)

            range_angle += swath/width

    # Remap and write
    dest = cv2.remap(image, xs, ys, cv2.INTER_LINEAR)
    cv2.imwrite(outname, dest)
