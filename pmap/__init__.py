import datetime as dt
from orbit_predictor.sources import NoradTLESource
from pmap.tle import check_tle_data
from pmap.georef import map_image

# Check that the TLE data is not stale
check_tle_data(False)
