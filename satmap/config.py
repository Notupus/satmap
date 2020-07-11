from orbit_predictor.locations import Location
import datetime as dt

# TLE management
tle_sources = [
    ("weather.tle", "https://celestrak.com/NORAD/elements/weather.txt")
]
tle_directory = "TLE/"
notify_old_tle = True
auto_update_tle = True
tle_lifetime = dt.timedelta(days=7)

# Earth size
earth_radius = 6371  # https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
polar_radius = 6356.8  # https://en.wikipedia.org/wiki/Earth_radius#Published_values IAU
equtorial_radius = 6378.1  # https://en.wikipedia.org/wiki/Earth_radius#Published_values IAU

# Ground station
location = None
location = Location("London", latitude_deg=51.507222, longitude_deg=-0.1275, elevation_m=24)
