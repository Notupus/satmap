import urllib.request
import shutil
import datetime as dt
import os
from satmap.config import tle_sources, auto_update_tle, notify_old_tle, tle_lifetime, tle_directory


def update_tle_data(quiet):
    '''
    update_tle_data(quiet)

    Downloads the TLE files specified in `config.py`.
    Doesn't output to `stdout` if quiet is set to `True`.
    '''
    if(not quiet):
        print("Downloading TLE Data")

    os.makedirs("TLE/", exist_ok=True)

    # Loop through TLE sources array
    for tle in tle_sources:
        if(not quiet):
            print("Downloading", tle[1])
        # Download as stream
        with urllib.request.urlopen(tle[1]) as response, open(os.path.join(tle_directory, tle[0]), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    # Save update time
    open(os.path.join(tle_directory, "updated_at"), "w").write(str(dt.datetime.now()))


def check_tle_data(quiet):
    '''
    valid = check_tle_data(quiet)

    Checks if the downloaded TLE data is still valid,
    returns `True` if TLE data is valid or auto updated and
    `True` if TLE data is out of date.
    Doesn't output to `stdout` if quiet is set to `True`.
    '''
    try:
        date = open(os.path.join(tle_directory, "updated_at"), "r").readline()
        age = dt.datetime.now() - dt.datetime.fromisoformat(date)
    except FileNotFoundError:
        age = dt.timedelta(days=100000)

    if(age > tle_lifetime):
        if(auto_update_tle):
            if(not quiet):
                print("TLE data is", age.days, "day(s) old\nAutomatically updating TLE data")
            update_tle_data(quiet)
            return True
        if(notify_old_tle):
            if(not quiet):
                print("Warning: TLE data is", (age - tle_lifetime).days, "days out of date")
            return False
    else:
        return True
