from datetime import datetime
import os
from typing import Dict, Union, AnyStr, List
import pandas as pd
from difflib import SequenceMatcher


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


def get_lat_long(place_name: str, parent_name: str = None):
    cities = pd.read_csv("cities.csv").apply(lambda x: x.str.capitalize() if x.dtype == "object" else x)
    districts = pd.read_csv("districts.csv").apply(lambda x: x.str.capitalize() if x.dtype == "object" else x)

    if place_name in cities["il_adi"].values and parent_name is None:
        return cities.loc[cities["il_adi"] == place_name][["lat", "lon"]].values[0].tolist()
    elif place_name in districts["ilce_adi"].values and parent_name is not None:
        return districts.loc[districts["ilce_adi"] == place_name][["lat", "lon"]].values[0].tolist()
    else:
        return None


def similarity_ratio(string1: str, string2: str) -> float:
    return SequenceMatcher(None, string1, string2).ratio()


def find_similar_place(place_name: str) -> Union[str, None]:
    districts = get_districts_from_file()
    similar_names: Dict[float, str] = {}

    def add_similar_name(name: str, score: float) -> None:
        if len(place_name) == len(name) and score > 0.5:
            similar_names[score] = name

    for city_name, city_districts in districts.items():
        city_similarity_score = similarity_ratio(place_name, city_name)
        add_similar_name(city_name, city_similarity_score)
        for district_name in city_districts:
            district_name = district_name.split(" ")[-1]
            district_similarity_score = similarity_ratio(place_name, district_name)
            add_similar_name(district_name, district_similarity_score)

    if not similar_names:
        return None
    return similar_names[max(similar_names.keys())]


def get_city_name(district_name: str) -> Union[str, None]:
    district_name = district_name.strip().capitalize()
    districts = pd.read_csv("districts.csv").apply(lambda x: x.str.capitalize() if x.dtype == "object" else x)
    cities = pd.read_csv("cities.csv").apply(lambda x: x.str.capitalize() if x.dtype == "object" else x)

    if district_name in districts["ilce_adi"].values:
        plate: int = districts.loc[districts["ilce_adi"] == district_name]["il_plaka"].values[0]
        return cities.loc[cities["plaka"] == plate]["il_adi"].values[0]
    else:
        return None
