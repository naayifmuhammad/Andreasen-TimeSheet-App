from datetime import datetime, timedelta



#latest code; if working disregard the rest

def get_dates_of_week_from_day(day, stringFormat = True):
    # Ensure the input is a datetime object
    if isinstance(day, str):
        day = datetime.strptime(day, "%Y-%m-%d")  # assuming the string is in 'YYYY-MM-DD' format

    # Find the Monday of the current week (weekday() returns 0 for Monday and 6 for Sunday)
    start_of_week = day - timedelta(days=day.weekday())

    # Generate the full week (Monday to Sunday)
    if stringFormat:
        week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    else:
        week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
        return week_dates
    
    # Return as a list of formatted date strings (optional)
    return [date.strftime("%Y-%m-%d") for date in week_dates]




#latest code; if working disregard the rest


def get_current_week_dates():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    current_week_dates = [start_of_week + timedelta(days=i) for i in range(5)]  # Monday to Friday
    return current_week_dates



#used for report generation (employee)
def getWeekDatesFromStartDate(date):
    # Calculate the start of the week (Monday)
    start_of_week = date - timedelta(days=date.weekday())
    # Create a list of dates for Monday to Friday
    #weekdates = [start_of_week + timedelta(days=i) for i in range(5)]
    weekdates = []
    for i in range(5):
        nextday = start_of_week + timedelta(days=i)
        weekdates.append(nextday.strftime("%d-%b"))
    return weekdates



def get_previous_week_dates():
    today = datetime.today()
    # Start of the current week (Monday)
    start_of_current_week = today - timedelta(days=today.weekday())
    # Start of the previous week (Monday)
    start_of_previous_week = start_of_current_week - timedelta(days=7)
    # List of dates from Monday to Friday of the previous week
    previous_week_dates = [start_of_previous_week + timedelta(days=i) for i in range(5)]
    return previous_week_dates


def get_current_and_previous_workweekranges():
    previous_week_dates = get_dates_of_week_from_day(datetime.today() - timedelta(days=7),False)
    current_week_dates = get_dates_of_week_from_day(datetime.today(),False)
    return {"previous" : previous_week_dates, "current" : current_week_dates}

def fetchWeekDropdown():
    week_choices = [(date.strftime('%Y-%m-%d'), date.strftime('%A')) for date in get_current_week_dates()]
    return week_choices
        
def get_current_work_week_full():
    full_week = get_current_week_dates()
    return {'start' : full_week[0].strftime('%d-%m-%y'), 'end' : full_week[-1].strftime('%d-%m-%y')}


def get_last_week_start() -> datetime:
    today = datetime.today()
    recent_monday = today - timedelta(days=today.weekday())
    last_week_start = recent_monday - timedelta(days=7)
    return last_week_start

def get_current_week_start()-> datetime:
    today= datetime.today()
    current_week_start = today - timedelta(days=today.weekday())
    return current_week_start

def get_last_week_end() -> datetime:
    last_monday = get_last_week_start()
    sunday = last_monday + timedelta(days=6)
    return sunday


def get_current_week_end() -> datetime:
     # Get today's date
    today = datetime.now()
    
    # Calculate the number of days to add to get to the last day of the week (Sunday)
    days_until_sunday = (6 - today.weekday())  # weekday() returns 0 for Monday, 1 for Tuesday, ..., 6 for Sunday
    
    # Calculate the date of the last day of the current week
    last_day_of_week = today + timedelta(days=days_until_sunday)
    
    return last_day_of_week.date()


def getTimePeriods(duration=None):
    if not duration:
        period ={'pStart': get_last_week_start(),'pEnd': get_last_week_end(),'cStart': get_current_week_start() , 'cEnd' : get_current_week_end()} 
        return period        
