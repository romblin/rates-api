from datetime import date, datetime, time

import pytz

moscow_tzinfo = pytz.timezone('Europe/Moscow')


def get_percent_change(x: float, y: float) -> float:
    return (y - x) / x * 100


def make_dt_from_date(d: date) -> datetime:
    return datetime.combine(d, time(14, 0))
