import datetime
import pytz
import ephem
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

# Ephemera character width
CHAR_WIDTH = 24*4

# ░▒▓

# Iterate over the date range and output ephemera
for day in closed_dates_interval(OBSERVER_BEG_DT, OBSERVER_END_DT):
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
        day.strftime("%Y-%m-%d"),
        sunrise.strftime("%H:%M:%S"),
        "{0:.3f}".format(sunrise_frac),
        sunset.strftime("%H:%M:%S"),
        "{0:.3f}".format(sunset_frac),
        "░"*round(sunrise_frac*CHAR_WIDTH) +
        "▓"*(round(sunset_frac*CHAR_WIDTH)-round(sunrise_frac*CHAR_WIDTH)) +
        "░"*(CHAR_WIDTH-round(sunset_frac*CHAR_WIDTH))
    )

# sunrise=OBS.previous_rising(ephem.Sun()) #Sunrise
# noon   =OBS.next_transit   (ephem.Sun(), start=sunrise) #Solar noon
# sunset =OBS.next_setting   (ephem.Sun()) #Sunset

# NOTE: remember how to calculate dawn/twilight
# We relocate the horizon to get twilight times
# OBS.horizon = '-6' #-6=civil twilight, -12=nautical, -18=astronomical
# beg_twilight=OBS.previous_rising(ephem.Sun(), use_center=True) #Begin civil twilight
# end_twilight=OBS.next_setting   (ephem.Sun(), use_center=True) #End civil twilight

