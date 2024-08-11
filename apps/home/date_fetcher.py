from datetime import datetime, timedelta

def get_current_week_dates():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    current_week_dates = [start_of_week + timedelta(days=i) for i in range(5)]  # Monday to Friday
    return current_week_dates

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
    return {"previous":get_previous_week_dates(), 'current': get_current_week_dates()}

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
    last_week_friday = last_monday + timedelta(days=6)
    return last_week_friday


def get_current_week_end() -> datetime:
    today = datetime.today()
    # Calculate the number of days to add to get to the next Friday
    days_until_friday = 4 - today.weekday()  # 4 corresponds to Friday
    current_week_end = today + timedelta(days=days_until_friday)
    return current_week_end

def getTimePeriods(duration=None):
    if not duration:
        period ={'pStart': get_last_week_start(),'pEnd': get_last_week_end(),'cStart': get_current_week_start() , 'cEnd' : get_current_week_end()} 
        return period        
