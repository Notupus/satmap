import datetime as dt
from orbit_predictor.sources import NoradTLESource
from satmap.tle import check_tle_data
from satmap.config import location

# Check that the TLE data is not stale
check_tle_data(False)

# Check that location is set
if location is None:
    raise Exception("Setup your location in satmap/config.py:20")
