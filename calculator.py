import datetime
import ephem
import pytz
import timezonefinder

# Set date range
BEG_DATE = "2018-01-01"
END_DATE = "2018-12-31"

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

import math

SUN = ephem.Sun()

OBSERVATION_HOUR = 12

ALTS = []
AZIS = []

for day in closed_dates_interval(OBSERVER_BEG_DT, OBSERVER_END_DT):

    # Analemma computation
    physical_timezone_delta = datetime.timedelta(hours=(float(OBS.lon) * 12 / math.pi))
    hour_o_clock = day.replace(tzinfo=None) \
                    + datetime.timedelta(hours=OBSERVATION_HOUR) \
                    - physical_timezone_delta
    OBS.date = hour_o_clock.strftime("%Y-%m-%d %H:%M:%S")
    SUN.compute(OBS)
    AZIS.append(SUN.az)
    ALTS.append(SUN.alt)

MAX_AZI = max(map(float, AZIS))
MIN_AZI = min(map(float, AZIS))
MAX_ALT = max(map(float, ALTS))
MIN_ALT = min(map(float, ALTS))

print("\def\EPH{")

for day in closed_dates_interval(OBSERVER_BEG_DT, OBSERVER_END_DT):

    # Analemma computation
    physical_timezone_delta = datetime.timedelta(hours=(float(OBS.lon) * 12 / math.pi))
    hour_o_clock = day.replace(tzinfo=None) \
                    + datetime.timedelta(hours=OBSERVATION_HOUR) \
                    - physical_timezone_delta
    OBS.date = hour_o_clock.strftime("%Y-%m-%d %H:%M:%S")
    SUN.compute(OBS)
    # AZIS.append(SUN.alt)
    # ALTS.append(SUN.az)

    # Ephemera calculation
    twelve_o_clock = day + datetime.timedelta(hours=12)
    # Set observer to 12:00 of day (in UTC)
    OBS.date = (twelve_o_clock).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    # Get sunrise/sunset in observer timezone
    sunrise = ephem.localtime(OBS.previous_rising(ephem.Sun())).astimezone(OBSERVER_TIMEZONE)
    sunset = ephem.localtime(OBS.next_setting(ephem.Sun())).astimezone(OBSERVER_TIMEZONE)
    # Get beginning/ending of day in observer timezone (needs to be re-localized after combining)
    beg_of_day = OBSERVER_TIMEZONE.localize(datetime.datetime.combine(day, datetime.time.min))
    end_of_day = OBSERVER_TIMEZONE.localize(datetime.datetime.combine(day, datetime.time.max))
    # Get sunrise/sunset as fraction normalized to day length
    sunrise_frac = (sunrise - beg_of_day) / (end_of_day - beg_of_day)
    sunset_frac = (sunset - beg_of_day) / (end_of_day - beg_of_day)

    print(
        ("\\eph" + "{{{}}}" * 9).format(
            day.strftime("%-j"),
            # day.strftime("%Y-%m-%d"),
            "{0:.3f}".format(SUN.alt),
            "{0:.3f}".format((SUN.alt-MIN_ALT)/(MAX_ALT-MIN_ALT)),
            "{0:.3f}".format(SUN.az),
            "{0:.3f}".format((SUN.az-MIN_AZI)/(MAX_AZI-MIN_AZI)),
            sunrise.strftime("%H:%M:%S"),
            "{0:.3f}".format(sunrise_frac),
            sunset.strftime("%H:%M:%S"),
            "{0:.3f}".format(sunset_frac)
        )
    )

print("}")

