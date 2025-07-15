# utility.py
from datetime import datetime, timedelta

def get_fpt_week_and_dates(today=None, fpt_start_date=None):
    if today is None:
        today = datetime.today().date()
    if fpt_start_date is None:
        fpt_start_date = datetime(2025, 6, 2).date()  # Monday of week 1
    
    if today.weekday() != 4:  # Friday check
        raise ValueError("Progress report can only be filled on Fridays.")
    
    delta_days = (today - fpt_start_date).days
    week_number = delta_days // 7 + 1
    
    start_of_week = today - timedelta(days=4)  # Monday of this week
    end_of_week = today  # Friday
    
    return week_number, start_of_week, end_of_week
