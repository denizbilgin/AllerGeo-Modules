from datetime import datetime
import os
from typing import Dict, Union, AnyStr, List


def is_valid_date(date_string: AnyStr) -> bool:
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False


def get_districts_from_file(filename: AnyStr = "aegean_districts.txt") -> Dict[AnyStr, List[AnyStr]]:
    if not os.path.exists(filename):
        return {}

    with open(filename, "r", encoding="utf-8") as f:
        current_city: Union[AnyStr, None] = None
        districts: Dict[AnyStr, List[AnyStr]] = {}
        for line in f:
            line = line.strip()

            if not line:
                current_city = None
                continue

            if current_city is None:
                current_city = line
                districts[current_city] = []
            else:
                districts[current_city].append(current_city + " " + line)
        return districts


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    celsius = (fahrenheit - 32) * 5 / 9
    return round(celsius, 2)


def inch_to_millimeter(inch: float) -> float:
    return inch * 25.4


def mph_to_kph(mph: float) -> float:
    return round(mph * 1.60934, 2)


def get_season(date: str) -> Union[AnyStr, None]:
    if not is_valid_date(date):
        return None
    date = datetime.fromisoformat(date)
    month = date.month
    if 3 <= month <= 5:
        return "Spring"
    elif 6 <= month <= 8:
        return "Summer"
    elif 9 <= month <= 11:
        return "Autumn"
    else:
        return "Winter"
