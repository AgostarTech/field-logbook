from datetime import timedelta

def working_days_since(start_date, current_date):
    """
    Count the number of working days (Monday-Friday) between start_date and current_date inclusive.
    """
    if current_date < start_date:
        return 0

    day_count = 0
    current = start_date
    while current <= current_date:
        if current.weekday() < 5:  # Monday=0, ..., Friday=4
            day_count += 1
        current += timedelta(days=1)
    return day_count
