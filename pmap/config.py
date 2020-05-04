import datetime as dt

## TLE Settings ##
tle_sources = [
    ("weather.tle", "https://celestrak.com/NORAD/elements/weather.txt")
]
tle_directory = "TLE/"
notify_old_tle = True
auto_update_tle = True
tle_lifetime = dt.timedelta(days = 5)

## Constants ##
earth_radius = 6371 # https://en.wikipedia.org/wiki/Earth_radius#Mean_radius

## Tweakables ##
segment_size = 32 # Size of transform segments, lower = higher quality transform