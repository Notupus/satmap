from math import *
import datetime as dt
from orbit_predictor import coordinate_systems
from PIL import Image
from numba import jit

from pmap.config import earth_radius, segment_size
from pmap.geomap import azimuth, reckon

'''
    x = map(x, in_min, in_max, out_min, out_max)

Map `x` in the range [`in_min`, `in_max`] to the range
[`out_min`, `out_max`] and clamp it to the boundaries.
'''
@jit(nopython=True)
def map(x, in_min, in_max, out_min, out_max):
    x = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if(x >= out_max): return out_max
    if(x <= out_min): return out_min
    return x

'''
    orbit = propergate_orbit(predictor, time, lines_per_second, rows)

Calculate the satellite prediction for each row of an image, where
`rows` is the number of rows to calculate, `time` is the calculation
start time and `predictor` is a orbit_predictor source. 
'''
def propergate_orbit(predictor, time, lines_per_second, rows):
    orbit = []
    for i in range(0, rows):
        orbit.append(coordinate_systems.ecef_to_llh(predictor.get_only_position(time)))
        time += dt.timedelta(seconds = 1/lines_per_second)
    return orbit

'''
Turn a straight line of (segment_size) pixels from a source image into
a non-straight line.
'''
def line_segment(dest, src, x, y, x1, y1, x2, y2):
    # Gradient of output line
    gradient = (y1-y2) / (x1-x2)
    # Length of output line (in x axis)
    x_length = ceil(abs(x1-x2))

    # Follow along the line
    for i in range(0, ceil(x_length)):
        dest[x1+i, y1+(gradient*i)] = src[x+(i/x_length*segment_size), y]

'''
do something, idk what
'''
def map_image(image_file, output_file, output_size, extent, swath_size, predictor, time, lines_per_second):
    # Source image
    src_image = Image.open(image_file)
    src_image = src_image.convert("RGB")
    src_width, src_height = src_image.size
    src_pixels = src_image.load()

    # Rendered image
    dest_image = Image.new("RGBA", output_size)
    dest_pixels = dest_image.load()

    # Calculate swath angle
    swath = swath_size / radians(earth_radius)
    
    # Calculate the satellite orbit over the course of the image
    orbit = propergate_orbit(predictor, time, lines_per_second, src_height)

    # Warp the image
    for y in range(1, src_height-1):
        # Perpendicular angle of satellite path at this point
        angle = azimuth(orbit[y-1][0], orbit[y-1][1], orbit[y+1][0], orbit[y+1][1]) + 90

        # Positions of segment edge in this row
        positions = []
        range_angle = -swath/2
        for x in range(0, src_width, segment_size):
            # Latitude and longitude of this pixel
            positions.append(reckon(orbit[y][0], orbit[y][1], range_angle, angle))
            range_angle += (swath/src_width)*segment_size

        # Do the deformation
        for i in range(0, len(positions)-1):
            line_segment(dest_pixels, src_pixels, i*segment_size, y,
                map(positions[i][1], extent[0], extent[1], 0, output_size[0]),
                map(positions[i][0], extent[3], extent[2], 0, output_size[1]),
                map(positions[i+1][1], extent[0], extent[1], 0, output_size[0]),
                map(positions[i+1][0], extent[3], extent[2], 0, output_size[1])
            )

    dest_image.save(output_file);

def create_underlay(image_file, output_file, swath_size, predictor, time, lines_per_second, map_filename):
    # Image input
    image = Image.open(image_file)
    width, height = image.size

    mapimg = Image.open(map_filename)
    mapimg = mapimg.convert("RGB")
    map_px = mapimg.load()
    mapw, maph = mapimg.size
    mapw /= 2
    maph /= 2

    # Canvas
    canvas = Image.new("RGBA", (width, height))
    pixels = canvas.load()

    # Calculate angle of swath
    swath = swath_size / radians(earth_radius)
    
    orbit = propergate_orbit(predictor, time, lines_per_second, height)
    for y in range(1, height-1):
        # Perpendicular angle of path
        angle = azimuth(orbit[y-1][0], orbit[y-1][1], orbit[y+1][0], orbit[y+1][1]) + 90

        range_angle = -swath/2
        for x in range(0, width):
            # Latitude and longitude of this pixel
            lat, lon = reckon(orbit[y][0], orbit[y][1], range_angle, angle)

            # Move pixel
            # TODO: a real transform, with something like matplotlib
            pixels[x, y] = px = map_px[(lon/180)*mapw + mapw, (-lat/90)*maph + maph]
            
            range_angle += swath/width
    
    canvas.save(output_file);