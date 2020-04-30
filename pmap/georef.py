from orbit_predictor import coordinate_systems
from pmap.config import earth_radius
from PIL import Image
from math import *
import datetime as dt
from pmap.geomap import azimuth, reckon
from numba import jit

'''
    x = map(x, in_min, in_max, out_min, out_max)

Map `x` in the range [`in_min`, `in_max`] to the range
[`out_min`, `out_max`]
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
`rows` is the number of rows to calculate, `lines_per_second` is
the number of lines per second, `time` is the calculation start time
and `predictor` is a orbit_predictor source. 
'''
def propergate_orbit(predictor, time, lines_per_second, rows):
    orbit = []
    for i in range(0, rows):
        orbit.append(coordinate_systems.ecef_to_llh(predictor.get_only_position(time)))
        time += dt.timedelta(seconds = 1/lines_per_second)
    return orbit

'''
    map_image(image_file, output_file, output_size, extent, swath_size, time, lines_per_second, predictor)

Turn a satellite image into a mercator mapped image, where `image_file` is
the filename of the image, `output_file` is the filename of the output file,
`output_size` is a tuple of width and height, `extent` is a tuple of the extent
of the output image, `swath_size` is the width of the swath in km, `time` is a
datetime object that represents the start of the image, `lines_per_second` is the
number of lines per second and `predictor` is a orbit_predictor source.
'''
def map_image(image_file, output_file, output_size, extent, swath_size, predictor, time, lines_per_second):
    # Image input
    image = Image.open(image_file)
    image = image.convert("RGB")
    width, height = image.size

    # Canvas
    canvas = Image.new("RGBA", output_size)
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
            pixels[map(lon, extent[0], extent[1], 0, output_size[0]), map(lat, extent[3], extent[2], 0, output_size[1])] = image.getpixel((x, height-y));
            
            range_angle += swath/width
    
    canvas.save(output_file);

def create_underlay(image_file, output_file, swath_size, predictor, time, lines_per_second, map_filename):
    # Image input
    image = Image.open(image_file)
    width, height = image.size

    mapimg = Image.open(map_filename)
    mapimg = mapimg.convert("RGB")
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
            pixels[x, y] = px = mapimg.getpixel(((lon/180)*mapw + mapw, (-lat/90)*maph + maph))
            
            range_angle += swath/width
    
    canvas.save(output_file);