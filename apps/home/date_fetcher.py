from datetime import datetime, timedelta

def get_current_week_dates():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(5)]  # Monday to Friday
    return week_dates

def fetchWeekDropdown():
    week_choices = [(date.strftime('%Y-%m-%d'), date.strftime('%A')) for date in get_current_week_dates()]
    return week_choices
        
def get_work_week():
    full_week = get_current_week_dates()
    return {'start' : full_week[0].strftime('%d-%m-%y'), 'end' : full_week[-1].strftime('%d-%m-%y')}
