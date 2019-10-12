import datetime
import pytz
import ephem
import timezonefinder

# Set date range
BEG_DATE = "2018-03-20"
END_DATE = "2018-12-21"

# Set hometown parameters
OBSERVER_LATITUDE = +45.23154
OBSERVER_LONGITUDE = +11.87498
OBSERVER_ELEVATION = 7 # metres

# Get timezone object from coordinates
TIMEZONE_FINDER = timezonefinder.TimezoneFinder()
OBSERVER_TIMEZONE_NAME = TIMEZONE_FINDER.timezone_at(lng=OBSERVER_LONGITUDE, lat=OBSERVER_LATITUDE)
OBSERVER_TIMEZONE = pytz.timezone(OBSERVER_TIMEZONE_NAME)

# Setup range extrema as timezoned datetimes
OBSERVER_BEG_DT = OBSERVER_TIMEZONE.localize(datetime.datetime.strptime(BEG_DATE, "%Y-%m-%d"))
OBSERVER_END_DT = OBSERVER_TIMEZONE.localize(datetime.datetime.strptime(END_DATE, "%Y-%m-%d"))

# Setup observer
OBS = ephem.Observer()
OBS.lat = str(OBSERVER_LATITUDE)
OBS.lon = str(OBSERVER_LONGITUDE)
OBS.elev = OBSERVER_ELEVATION

# Date range helper
def closed_dates_interval(start_date, end_date):
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + datetime.timedelta(days=n)

import matplotlib.pyplot as plt
import math


sun = ephem.Sun()

# Iterate over the date range and output ephemera
for hour in range (12,13):
    X = []
    Y = []
    for day in closed_dates_interval(OBSERVER_BEG_DT, OBSERVER_END_DT):

        # hour_o_clock = day + datetime.timedelta(hours=hour)
        # corrected = (hour_o_clock - physical_timezone_delta).astimezone(pytz.utc)

        physical_timezone_delta = datetime.timedelta(hours=(float(OBS.lon) * 12 / math.pi))
        hour_o_clock = day.replace(tzinfo=None) \
                       + datetime.timedelta(hours=hour) \
                       - physical_timezone_delta
        OBS.date = hour_o_clock.strftime("%Y-%m-%d %H:%M:%S")

        sun.compute(OBS)
        Y.append(sun.alt)
        X.append(sun.az)

    plt.scatter(X,Y, label=hour_o_clock)

plt.legend()
plt.grid(True)


plt.show()
