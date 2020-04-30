import datetime as dt

tle_sources = [
    ("weather.tle", "https://celestrak.com/NORAD/elements/weather.txt")
]
tle_directory = "TLE/"
notify_old_tle = True
auto_update_tle = True
tle_lifetime = dt.timedelta(days = 5)

# I doubt this will need changing any time soon
# https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
earth_radius = 6371
