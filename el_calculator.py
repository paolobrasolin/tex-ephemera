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

print("\def\EPH{")

for day in closed_dates_interval(OBSERVER_BEG_DT, OBSERVER_END_DT):

    # Ephemera calculation
    twelve_o_clock = day + datetime.timedelta(hours=12)
    # Set observer to 12:00 of day (in UTC)
    OBS.date = (twelve_o_clock).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

    OBS.horizon = '0'
    sun_rise = OBS.previous_rising(ephem.Sun())
    sun_noon = OBS.next_transit(ephem.Sun(), start=sun_rise)
    sun_down = OBS.next_setting(ephem.Sun())
    OBS.horizon = '-6'
    civ_dawn = OBS.previous_rising(ephem.Sun(), use_center=True)
    civ_dusk = OBS.next_setting(ephem.Sun(), use_center=True)
    OBS.horizon = '-12'
    nau_dawn = OBS.previous_rising(ephem.Sun(), use_center=True)
    nau_dusk = OBS.next_setting(ephem.Sun(), use_center=True)
    OBS.horizon = '-18'
    ast_dawn = OBS.previous_rising(ephem.Sun(), use_center=True)
    ast_dusk = OBS.next_setting(ephem.Sun(), use_center=True)

    # Localize
    sun_rise = ephem.localtime(sun_rise).astimezone(OBSERVER_TIMEZONE)
    sun_noon = ephem.localtime(sun_noon).astimezone(OBSERVER_TIMEZONE)
    sun_down = ephem.localtime(sun_down).astimezone(OBSERVER_TIMEZONE)
    civ_dawn = ephem.localtime(civ_dawn).astimezone(OBSERVER_TIMEZONE)
    civ_dusk = ephem.localtime(civ_dusk).astimezone(OBSERVER_TIMEZONE)
    nau_dawn = ephem.localtime(nau_dawn).astimezone(OBSERVER_TIMEZONE)
    nau_dusk = ephem.localtime(nau_dusk).astimezone(OBSERVER_TIMEZONE)
    ast_dawn = ephem.localtime(ast_dawn).astimezone(OBSERVER_TIMEZONE)
    ast_dusk = ephem.localtime(ast_dusk).astimezone(OBSERVER_TIMEZONE)

    # Get beginning/ending of day in observer timezone (needs to be re-localized after combining)
    beg_of_day = OBSERVER_TIMEZONE.localize(datetime.datetime.combine(day, datetime.time.min))
    end_of_day = OBSERVER_TIMEZONE.localize(datetime.datetime.combine(day, datetime.time.max))

    # Normalize
    sun_rise_frac = (sun_rise - beg_of_day) / (end_of_day - beg_of_day)
    sun_noon_frac = (sun_noon - beg_of_day) / (end_of_day - beg_of_day)
    sun_down_frac = (sun_down - beg_of_day) / (end_of_day - beg_of_day)
    civ_dawn_frac = (civ_dawn - beg_of_day) / (end_of_day - beg_of_day)
    civ_dusk_frac = (civ_dusk - beg_of_day) / (end_of_day - beg_of_day)
    nau_dawn_frac = (nau_dawn - beg_of_day) / (end_of_day - beg_of_day)
    nau_dusk_frac = (nau_dusk - beg_of_day) / (end_of_day - beg_of_day)
    ast_dawn_frac = (ast_dawn - beg_of_day) / (end_of_day - beg_of_day)
    ast_dusk_frac = (ast_dusk - beg_of_day) / (end_of_day - beg_of_day)

    print(
        ("\\eph" + "{{{}}}" * 9).format(
            day.strftime("%-j"),
            "{0:.4f}".format(ast_dawn_frac),
            "{0:.4f}".format(nau_dawn_frac),
            "{0:.4f}".format(civ_dawn_frac),
            "{0:.4f}".format(sun_rise_frac),
            # "{0:.4f}".format(sun_noon_frac),
            "{0:.4f}".format(sun_down_frac),
            "{0:.4f}".format(civ_dusk_frac),
            "{0:.4f}".format(nau_dusk_frac),
            "{0:.4f}".format(ast_dusk_frac)
        )
    )

print("}")

