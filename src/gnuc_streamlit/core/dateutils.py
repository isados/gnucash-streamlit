"""Date Utilities"""
from datetime import date
from dateutil.relativedelta import relativedelta

def _to_isoformat(*dates: date) -> str:
    return tuple(d.isoformat() for d in dates)
    

def get_weeks(d: date):

    month_start = d - relativedelta(days=d.day-1)
    month_end = month_start + relativedelta(months=1, days=-1)
    
    days_in_current_month = (month_end - month_start).days
    weeks = []
    for index in range(0, days_in_current_month, 7):
        week_start = month_start+relativedelta(days=index)

        week_end = week_start+relativedelta(days=6)
        week_end = min(month_end, week_end)
        weeks.append((week_start, week_end))
    return weeks

def get_current_week(d: date=None) -> str:
    """Gets the Week-Ends for a Date"""
    if not d:
        d = date.today()
    END = 1
    for week in get_weeks(d):
        if week[END] >= d:
            return _to_isoformat(*week)


def get_month(past:int=0) -> tuple:
    "Get Month_Start & Month_End from `past`"
    sel_day = date.today()
    if past:
        sel_day = sel_day - relativedelta(months=past)

    month_start = sel_day - relativedelta(days=sel_day.day-1)
    month_end = month_start + relativedelta(months=1, days=-1)
    return _to_isoformat(month_start, month_end)

def get_current_month() -> tuple:
    return get_month(0)



if __name__ == '__main__':
    d = date(2023, 11, 30)
    print(get_current_week(d))
    print(get_current_month())
