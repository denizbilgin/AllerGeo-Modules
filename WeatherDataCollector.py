import os.path
import time
from abc import ABC, abstractmethod
from typing import Union, Optional, AnyStr
import requests
from Utils import *
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from UnicodeTR import UnicodeTR
from DatabaseHandler import DatabaseHandler


class WeatherDataCollector(ABC):
    def __init__(self, districts_filename: AnyStr):
        self.districts = get_districts_from_file(districts_filename)

    @abstractmethod
    def get_data(self, place_name: AnyStr) -> Union[List[Dict], Dict]:
        raise NotImplementedError("You need to implement get_pollen_data function.")

    @abstractmethod
    def save(self, data: Union[List[Dict], Dict], filename: AnyStr) -> None:
        raise NotImplementedError("You need to implement save function.")


class AccuWeather(WeatherDataCollector):
    def __init__(self, districts_filename: AnyStr = "aegean_districts.txt"):
        super().__init__(districts_filename)
        self.api_keys = ["b7AQGWXepTAyjzsvgg8rcoo01lPIQrhQ",
                         "fcgGMMOJQqJmRFupwfABKB9DNHcYAObK",
                         "rGQakzk0rn26wOrrjLVVZu45VYAKFSzT",
                         "lMS2eVUQQGkkWrlbbA7aLyqj6T9GTsT0",
                         "z6yxRXVsgTah7V703Fzmzfdn4y1lA3y0",
                         "svYG8IJktMUVEQKyq2w8AAVBJyBKzuSh",
                         "JG9SWbeazzw1fd5fCmtJAut2wplFaAvA",
                         "tTI76aksjDjbAAJJVfmQ5zMx9sgN9jKp",
                         "5kc8ObMmCuDSOkUrsdl2R2Lgj7krAvfy",
                         "XmxKp8p7t1aQAIMA0qUYNOrAGvsxZZBA",
                         "IdcH6C5JwGdonwqVCFGUhTapyAXm0GqE",
                         "COkfPtV5UDjKJBYTDXu1ky7fVIbDZZL8",
                         "RHhgHFC4flvViNeQyyLMW7Rjzqi2hAgg",
                         "3NxZD92F2KJFrxfcdLAvcXEK3G8wZvkv",
                         "jsy15OjqNfTa8zbp0pE1vqdXtISOKjLd",
                         "WLDB8sG0RGOe0wkL3mNG1W0owvVyvU2u",
                         "FJ18uXJfYSayZIeXjfeti3u9syEejjje",
                         "za0raAko4C5HjzCG9IQqkyyaPZnXNVXT",
                         "uMxWyAs21GYgeavcl3OUyqswMf9W30zT",
                         "Dfju9fcL2Dlgkr1IWIK9zkSEs4EEMvR8",
                         "fLAjqb66dljVA6O0LGUHgej3c7RY52av",
                         "HWQa5hLGwNtRREuBXWEAYDkEcoZ70Gcz",
                         "YtIohEhU4ouqqaguYVaYTub6AO1yAwEi",
                         "eD3AbxQiGkXyGmPOvn76maxym3BcWgaM",
                         "1z31Af8TWrCGtwwkvG0a5SZbSG1J7UL2",
                         "YBIidwpLsAjyQPKvdhtmV9CX1aEHxgBQ",
                         "w8ANdGxNyhcAdKLMvXuVT1X4AlZgy6KV",
                         "Gm1UR3uIR4QGBHAOE4BxqOJW1rfxKDff",
                         "2WqRYT7tuPahRLU6eA8Rnky99Y6Daftw",
                         "aA1gkMRNNZEV5GEOVtgi0hSYCbEQCCPC",
                         "HmIQTvA2tMpqggorVmB75w0A6WXG5lnY",
                         "gfCD2f2MAGWqAQO2BsU0MqLHpOSHKfOr",
                         "NQAtiFrvvJ1GFpRLkT8gvMzXnbjnN7mt",
                         "tHzRDptBzfXpRg2pv67x9GjbirnvKX3F"]
        self.available_api_key_index = 0
        self.redundant_columns = ["EpochDate", "Sources", "MobileLink", "Link", "Sun_EpochRise", "Sun_EpochSet", "Moon_EpochRise", "Moon_EpochSet",
                                  "Day_Icon", "Day_Wind_Direction_English", "Day_WindGust_Direction_English", "Night_Icon",
                                  "Night_Wind_Direction_English", "Night_WindGust_Direction_English"]
        self.fahrenheit_unit_columns = ["Temperature_Minimum_Value", "Temperature_Maximum_Value", "RealFeelTemperature_Minimum_Value",
                                        "RealFeelTemperature_Maximum_Value", "RealFeelTemperatureShade_Minimum_Value",
                                        "RealFeelTemperatureShade_Maximum_Value", "DegreeDaySummary_Heating_Value", "DegreeDaySummary_Cooling_Value",
                                        "Day_WetBulbTemperature_Minimum_Value", "Day_WetBulbTemperature_Maximum_Value", "Day_WetBulbTemperature_Average_Value",
                                        "Day_WetBulbGlobeTemperature_Minimum_Value", "Day_WetBulbGlobeTemperature_Maximum_Value", "Day_WetBulbGlobeTemperature_Average_Value",
                                        "Night_WetBulbTemperature_Minimum_Value", "Night_WetBulbTemperature_Maximum_Value", "Night_WetBulbTemperature_Average_Value",
                                        "Night_WetBulbGlobeTemperature_Minimum_Value", "Night_WetBulbGlobeTemperature_Maximum_Value",
                                        "Night_WetBulbGlobeTemperature_Average_Value"]
        self.mph_unit_columns = ["Day_Wind_Speed_Value", "Day_WindGust_Speed_Value", "Night_Wind_Speed_Value", "Night_WindGust_Speed_Value"]
        self.in_unit_columns = ["Day_TotalLiquid_Value", "Day_Rain_Value", "Day_Snow_Value", "Day_Ice_Value", "Day_Evapotranspiration_Value",
                                "Night_TotalLiquid_Value", "Night_Rain_Value", "Night_Snow_Value", "Night_Ice_Value", "Night_Evapotranspiration_Value"]

        # For Selenium
        self.base_website_url = "https://www.accuweather.com/en/en/"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--force-device-scale-factor=0.3")
        self.driver = webdriver.Chrome(service=Service("chromedriver/chromedriver.exe"), options=self.chrome_options)

    def get_data(self, place_name: AnyStr) -> Union[List[Dict], Dict]:
        place_name = UnicodeTR(place_name.strip()).lower()
        if len(place_name) < 1:
            raise ValueError("Please provide a real district name.")
        location_key = self.__get_location_key(place_name)

        # Getting pollen information by location key from API
        pollen_url = f"https://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
        pollen_params = {
            'apikey': self.api_keys[self.available_api_key_index],
            'details': 'true',
        }

        response = requests.get(pollen_url, params=pollen_params)
        if response.status_code == 200:
            pollen_data = response.json()
            if 'DailyForecasts' in pollen_data and len(pollen_data['DailyForecasts']) > 0:
                measurements: Dict = pollen_data["DailyForecasts"][0]
                measurements.update(self.__get_health_activities_data(place_name, location_key))
                return measurements
        else:
            if response.status_code == 503:
                self.__increment_api_index()
                return self.get_data(place_name)

    def save(self, data: Union[List[Dict], Dict], table_name: AnyStr) -> None:
        db_handler = DatabaseHandler("./config.json", table_name, self.redundant_columns, self.fahrenheit_unit_columns,
                                     self.mph_unit_columns, self.in_unit_columns)
        db_handler.save_to_database(data)

    def save_aegean(self, table_name: AnyStr) -> None:
        forecasts = []
        db_handler = DatabaseHandler("./config.json", table_name, self.redundant_columns, self.fahrenheit_unit_columns,
                                     self.mph_unit_columns, self.in_unit_columns)

        for city_name, city_districts in self.districts.items():
            city_data = self.get_data(city_name)
            city_data["City"] = city_name
            city_data["District"] = None
            city_data["Season"] = get_season(city_data["Date"])

            city_data["CityId"] = db_handler.fetch_city_id_by_name(city_name)
            city_data["DistrictId"] = None
            forecasts.append(city_data)

            for city_district in city_districts:
                district_data = self.get_data(city_district)
                district_data["City"] = city_name
                district_data["District"] = city_district.split(" ")[-1]
                district_data["Season"] = get_season(district_data["Date"])

                district_data["CityId"] = city_data["CityId"]
                district_data["DistrictId"] = db_handler.fetch_district_id_by_name(city_district)
                forecasts.append(district_data)
        self.save(forecasts, table_name)

    def __get_location_key(self, district_name: AnyStr) -> AnyStr:
        location_url = f"https://dataservice.accuweather.com/locations/v1/cities/search"
        params = {
            'apikey': self.api_keys[self.available_api_key_index],
            'q': district_name
        }
        response = requests.get(location_url, params=params)
        if response.status_code == 503:
            self.__increment_api_index()
            return self.__get_location_key(district_name)

        location_data = response.json()
        location_key = location_data[0]['Key']
        print(f"Location Key for {UnicodeTR(district_name).capitalize()}: {location_key}")
        return location_key

    def __increment_api_index(self) -> None:
        self.available_api_key_index += 1
        print(f"API key index is incremented to {self.available_api_key_index}. You have {(len(self.api_keys) - 1) - (self.available_api_key_index - 1)} API keys left.")
        if self.available_api_key_index == len(self.api_keys) - 1:
            raise Exception("All API keys are exceeded quota. Add new API key to api_keys variable.")

    def __get_health_activities_data(self, district_name: AnyStr, location_key: AnyStr) -> Dict:
        health_activities_url = f"{self.base_website_url}{district_name}/{location_key}/health-activities/{location_key}"
        self.driver.get(health_activities_url)

        content = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )
        lifestyle_index_lists = content.find_elements(By.CLASS_NAME,"lifestyle-index-list")
        lifestyles_dict: Dict = {}

        time.sleep(4)
        for lifestyle_list in lifestyle_index_lists:
            title = lifestyle_list.find_element(By.CLASS_NAME, "index-list-title").text
            title = title.replace(" ", "").replace("&", "And")
            cards_container = lifestyle_list.find_element(By.CLASS_NAME, "index-list-cards-container")
            cards = cards_container.find_elements(By.TAG_NAME, "a")

            for card in cards:
                #time.sleep(3)
                #print(card.text)
                card_name, card_value = card.text.split("\n")
                card_name = card_name.replace(" ", "").replace("&", "And")
                lifestyles_dict[title + "_" + card_name] = card_value

        del lifestyles_dict["Allergies_TreePollen"], lifestyles_dict["Allergies_RagweedPollen"], lifestyles_dict["Allergies_Mold"], lifestyles_dict["Allergies_GrassPollen"]
        dust_and_dander_value = lifestyles_dict.pop("Allergies_DustAndDander")
        lifestyles_dict["AirAndPollen_DustAndDander"] = dust_and_dander_value
        return lifestyles_dict
