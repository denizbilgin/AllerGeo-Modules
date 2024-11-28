from datetime import datetime
import os
from typing import Dict, AnyStr, List, Optional
import pandas as pd
from difflib import SequenceMatcher
from UnicodeTR import UnicodeTR
from googletrans import Translator


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
        current_city: Optional[AnyStr] = None
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
    millimeter = inch * 25.4
    return millimeter


def mph_to_kph(mph: float) -> float:
    kph = round(mph * 1.60934, 2)
    return kph


def get_season(date: AnyStr) -> Optional[AnyStr]:
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


def get_lat_long(place_name: AnyStr, parent_name: AnyStr = None) -> Optional[Dict[AnyStr, float]]:
    cities = pd.read_csv("cities.csv")
    districts = pd.read_csv("districts.csv")

    cities = cities.map(lambda x: UnicodeTR(x).capitalize() if isinstance(x, str) else x)
    districts = districts.map(lambda x: UnicodeTR(x).capitalize() if isinstance(x, str) else x)

    if place_name in cities["il_adi"].values and parent_name is None:
        data = cities.loc[cities["il_adi"] == place_name]
        coordinates: Dict[AnyStr, Dict] = data[["lat", "lon", "northeast_lat", "northeast_lon", "southwest_lat", "southwest_lon"]].to_dict()
        result_dict: Dict[AnyStr, float] = {key: value[data["plaka"].iloc[0] - 1] for key, value in coordinates.items()}
        return result_dict
    elif place_name in districts["ilce_adi"].values and parent_name is not None:
        data = districts.loc[districts["ilce_adi"] == place_name]
        coordinates: Dict[AnyStr, Dict] = data[["lat", "lon", "northeast_lat", "northeast_lon", "southwest_lat", "southwest_lon"]].to_dict()
        result_dict: Dict[AnyStr, float] = {key: value[data["ilce_id"].iloc[0] - 1] for key, value in coordinates.items()}
        return result_dict
    else:
        return None


def similarity_ratio(string1: AnyStr, string2: AnyStr) -> float:
    return SequenceMatcher(None, string1, string2).ratio()


def find_similar_place(place_name: AnyStr, similarity_threshold: float = 0.3) -> Optional[AnyStr]:
    districts = get_districts_from_file()
    similar_names: Dict[float, AnyStr] = {}

    def add_similar_name(name: AnyStr, score: float) -> None:
        if len(place_name) == len(name) and score > similarity_threshold:
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


def get_city_name(district_name: AnyStr) -> Optional[AnyStr]:
    district_name = UnicodeTR(district_name.strip()).capitalize()
    districts = pd.read_csv("districts.csv").map(lambda x: UnicodeTR(x).capitalize() if isinstance(x, str) else x)
    cities = pd.read_csv("cities.csv").map(lambda x: UnicodeTR(x).capitalize() if isinstance(x, str) else x)

    if district_name in districts["ilce_adi"].values:
        plate: int = districts.loc[districts["ilce_adi"] == district_name]["il_plaka"].values[0]
        return cities.loc[cities["plaka"] == plate]["il_adi"].values[0]
    else:
        return None


def translate_to_turkish(common_names: Dict[AnyStr, AnyStr], languages_priority: List[AnyStr] = ["fra", "eng", "deu"]) -> AnyStr:
    translator = Translator()
    for lang in languages_priority:
        if lang in common_names.keys():
            text_to_translate = common_names[lang]
            translation = translator.translate(text=text_to_translate, src=lang[:-1], dest="tr")
            return translation.text

    if common_names:
        text_to_translate = next(iter(common_names.values()))
        translation = translator.translate(text_to_translate, src='auto', dest='tr')
        return translation.text

    return "No translation available."
