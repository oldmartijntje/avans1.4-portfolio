import pandas as pd
from datetime import date, datetime, timedelta

# Start and end dates
start_date = datetime(1970, 1, 1)
end_date   = datetime(2025,12,31)

# Generate date range
dates = pd.date_range(start=start_date, end=end_date)

# Function to determine season
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

# Anonymous Gregorian algorithm for Easter Sunday
def calculate_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day   = ((h + l - 7*m + 114) % 31) + 1
    return date(year, month, day)

# Build the base DataFrame
df = pd.DataFrame({'date': dates})
df['year']      = df['date'].dt.year
df['month']     = df['date'].dt.month_name()
df['day']       = df['date'].dt.day
df['weekday']   = df['date'].dt.day_name()
df['season']    = df['date'].dt.month.map(get_season)
df['is_weekend']= df['date'].dt.weekday >= 5

# --- build holiday lookup ---
holiday_list = []

for y in df['year'].unique():
    # === Moveable feasts ===
    easter = calculate_easter(y)
    good_friday = easter - timedelta(days=2)
    easter_monday = easter + timedelta(days=1)
    ascension = easter + timedelta(days=39)
    whit_sunday = easter + timedelta(days=49)
    whit_monday = easter + timedelta(days=50)

    holiday_list.extend([
        (good_friday,          'Goede Vrijdag'),
        (easter,               'Eerste Paasdag'),
        (easter_monday,        'Tweede Paasdag'),
        (ascension,            'Hemelvaartsdag'),
        (whit_sunday,          'Eerste Pinksterdag'),
        (whit_monday,          'Tweede Pinksterdag'),
    ])

    # === Fixed-date holidays ===
    holiday_list.extend([
        (date(y, 1, 1),        'Nieuwjaarsdag'),
        (date(y, 12, 25),      'Eerste Kerstdag'),
        (date(y, 12, 26),      'Tweede Kerstdag'),
    ])



    # === Queen's Day (1949–2013), adjust for Sundays
    if 1949 <= y <= 2013:
        queens_day = date(y, 4, 30)
        if queens_day.weekday() == 6:  # Sunday
            queens_day = date(y, 5, 1) if y < 1980 else date(y, 4, 29)
        holiday_list.append((queens_day, 'Koninginnedag'))

    # === King's Day (2014– ), adjust for Sundays
    if y >= 2014:
        kings_day = date(y, 4, 27)
        if kings_day.weekday() == 6:  # Sunday
            kings_day = date(y, 4, 26)
        holiday_list.append((kings_day, 'Koningsdag'))

# turn into dict for fast lookup
holiday_dict = {d: name for d, name in holiday_list}

# Map into DataFrame (will give NaN where no holiday)
df['holiday'] = df['date'].dt.date.map(holiday_dict)

# isMyBirthday: true on Sept 5th for year ≥ 2005
df['isMyBirthday'] = (
    (df['date'].dt.month == 9) &
    (df['date'].dt.day   == 5) &
    (df['date'].dt.year  >= 2005)
)

# Save to CSV
df.to_csv('calendar_dataset_1970_2025_with_holidays.csv', index=False)

