from pmap.georef import map_image
import argparse
import datetime as dt
from orbit_predictor.sources import NoradTLESource
from pmap.tle import update_tle_data
from pmap.georef import map_image, create_underlay

parser = argparse.ArgumentParser()
parser.add_argument('-u', help='manually update TLE data', action='store_true', dest='UPDATE', default=False)
parser.add_argument('-s', help='swath size of the satellite (in km)', type=int, dest='SWATH_SIZE', default=2800)
parser.add_argument('-l', help='the number of lines per second', type=int, dest='LINES_PER_SECOND', default=2)
parser.add_argument('-T', help='path to TLE file', type=str, dest='FILENAME', default="TLE/weather.tle")
parser.add_argument('-a', help='top-left of the mapped image', type=str, dest='POS1', default="-180,-90")
parser.add_argument('-b', help='bottom-right of the mapped image', type=str, dest='POS2', default="180,90")
parser.add_argument('-t', help='time of the start of image (in ISO format)', type=str, dest='ISO_TIME', required=True)
parser.add_argument('-n', help='name of satellite', type=str, dest='NAME', default="NOAA 19")
parser.add_argument('-S', help='size of output image', type=str, dest='SIZE', default="2880x1440")
parser.add_argument('-i', help='input filename', type=str, dest='IN_FILENAME', required=False)
parser.add_argument('-o', help='output filename', type=str, dest='OUT_FILENAME', required=True)
parser.add_argument('-m', help='map filename (changes output type to underlay)', type=str, dest='MAP_FILENAME')
parser.add_argument('-r', help='rotation of satellite', type=float, dest='SKEW', default=1.5)


args = parser.parse_args()

if(args.UPDATE):
    update_tle_data(False)
    exit()

# Load orbital parameters
source = NoradTLESource.from_file(filename=args.FILENAME)
predictor = source.get_predictor(args.NAME)

# String manipulation
size = args.SIZE.split("x")
topleft = args.POS1.split(",")
bottomright = args.POS2.split(",")

if(args.MAP_FILENAME is None):
    map_image(
        args.IN_FILENAME,  # Input file
        args.OUT_FILENAME,
        (int(size[0]), int(size[1])),  # Output file size
        (int(topleft[0]), int(bottomright[0]), int(topleft[1]), int(bottomright[1])),  # Extent of the output image (min_lon, max_lon, min_lat, max_lat)
        int(args.SWATH_SIZE),  # Swath size in km
        predictor,  # The predictor
        dt.datetime.fromisoformat(args.ISO_TIME),  # Beginning of image
        int(args.LINES_PER_SECOND),  # Lines per second
        float(args.SKEW)
    )
else:
    create_underlay(
        (int(size[0]), int(size[1])),
        args.OUT_FILENAME,
        int(args.SWATH_SIZE),  # Swath size in km
        predictor,  # The predictor
        dt.datetime.fromisoformat(args.ISO_TIME),  # Beginning of image
        int(args.LINES_PER_SECOND),  # Lines per second
        args.MAP_FILENAME,
        float(args.SKEW)
    )
