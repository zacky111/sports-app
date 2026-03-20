from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import calendar as cal


def get_month_calendar(year: int, month: int) -> List[List[Tuple[int, str]]]:
    """
    Zwraca kalendarz miesiąca jako lista tygodni.
    Każdy dzień to (dzień, data_w_formacie_YYYY-MM-DD) lub (0, "") dla dni z innych miesięcy
    """
    month_calendar = cal.monthcalendar(year, month)
    result = []
    
    for week in month_calendar:
        week_dates = []
        for day in week:
            if day == 0:
                week_dates.append((0, ""))
            else:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                week_dates.append((day, date_str))
        result.append(week_dates)
    
    return result


def get_month_name(month: int, lang: str = "pl") -> str:
    """Zwraca nazwę miesiąca"""
    months_pl = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]
    months_en = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    if lang == "pl":
        return months_pl[month - 1]
    return months_en[month - 1]


def get_weekday_names(lang: str = "pl") -> List[str]:
    """Zwraca nazwy dni tygodnia"""
    if lang == "pl":
        return ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
