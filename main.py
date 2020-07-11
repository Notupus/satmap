#!/usr/bin/python3
from orbit_predictor.sources import NoradTLESource
from orbit_predictor import coordinate_systems
import datetime as dt
from math import *
import argparse

from satmap.georef import make_map
from satmap.config import location

# FIXME: does this even work
def isnorthbound(sat_pass):
    aos = coordinate_systems.ecef_to_llh(predictor.get_only_position(sat_pass.aos))
    los = coordinate_systems.ecef_to_llh(predictor.get_only_position(sat_pass.los))
    return aos[1] < los[1]

# Parse arguments
parser = argparse.ArgumentParser(prog='satmap',
                                 description='Make map overlays for polar satellites')

parser.add_argument('filename', metavar='path', type=str,
                    help='path to the output map')
parser.add_argument('-s', '--satellite', dest='sat', type=str, default="NOAA 19",
                    help='name of satellite')
parser.add_argument('-t', '--time', dest='time', type=str, required=True,
                    help='any time before the pass (ISO time)')

args = parser.parse_args()

source = NoradTLESource.from_file(filename="TLE/weather.tle")
predictor = source.get_predictor(args.sat)

time = dt.datetime.fromisoformat(args.time)

sat_pass = predictor.get_next_pass(location, when_utc=time)
print("Satellite: {}\nPass start: {}\nDuration: {}s\nElevation: {}\nDirection: {}".format(
    args.sat,
    sat_pass.aos,
    floor(sat_pass.duration_s),
    round(sat_pass.max_elevation_deg),
    "northbound" if isnorthbound(sat_pass) else "southbound"
))

sat_swath = 2935
sat_lps = 2
width = 909
height = int(sat_pass.duration_s * sat_lps)

make_map(predictor, sat_swath, sat_lps, width, height, sat_pass.aos, args.filename)
