import ast
from abc import ABC, abstractmethod
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict


class WeatherDataCollector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, district: str, date: str, date_range: int = 4) -> List[Dict]:
        raise NotImplementedError("You need to implement get_pollen_data function.")

    @abstractmethod
    def save(self, data: Dict, filename: str):
        raise NotImplementedError("You need to implement save function.")


class WeatherCollectorSelenium(WeatherDataCollector):
    def __init__(self):
        super().__init__()
        self.API_KEY = "za0raAko4C5HjzCG9IQqkyyaPZnXNVXT"

    def get_data(self, district_name: str, date: str, date_range: int = 4) -> List[Dict]:
        date = datetime.strptime(date, "%Y-%m-%d")
        dates = [date + timedelta(days=i) for i in range(-date_range, date_range + 1)]

        district_name = district_name.lower().strip()
        if len(district_name) < 1:
            raise ValueError("Please provide a real district name.")

        location_key = self.__get_location_key(district_name)
        forecasts = []

        for date in dates:
            formatted_date = date.strftime("%Y%m%d")

            # Getting pollen information by location key from API
            pollen_url = f"https://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
            pollen_params = {
                'apikey': self.API_KEY,
                'details': 'true',
            }

            response = requests.get(pollen_url, params=pollen_params)
            if response.status_code == 200:
                pollen_data = response.json()

                if 'DailyForecasts' in pollen_data and len(pollen_data['DailyForecasts']) > 0:
                    forecast = pollen_data['DailyForecasts'][0]
                    forecast["Date"] = date
                    forecasts.append(forecast)
            else:
                raise Exception(f"Could not get data for {formatted_date}. Status Code: {response.status_code}")

        return forecasts

    def save(self, data: List[Dict], filename: str):
        normalized_daily_dataframes = []

        for day_data in data:
            normalized_dataframe = pd.json_normalize(day_data, sep="_")

            if "AirAndPollen" in normalized_dataframe.columns:
                air_and_pollen = normalized_dataframe["AirAndPollen"].apply(pd.Series)
                air_and_pollen.columns = [f"AirAndPollen_{item["Name"]}" for item in air_and_pollen.iloc[0]]

                for column in air_and_pollen.columns:
                    air_and_pollen[column] = air_and_pollen[column].apply(lambda x: x['Category'] if isinstance(x, dict) else x)

                normalized_dataframe = pd.concat([normalized_dataframe.drop(columns=["AirAndPollen"]), air_and_pollen], axis=1)
            normalized_daily_dataframes.append(normalized_dataframe)

        final_dataframe = pd.concat(normalized_daily_dataframes, ignore_index=True)
        final_dataframe.to_csv(filename, index=False)

    def __get_location_key(self, district_name: str) -> str:
        location_url = f"https://dataservice.accuweather.com/locations/v1/cities/search"
        params = {
            'apikey': self.API_KEY,
            'q': district_name
        }
        response = requests.get(location_url, params=params)
        if response.status_code == 503:
            raise Exception("Quota exceeded.")

        location_data = response.json()
        location_key = location_data[0]['Key']
        print(f"Location Key for {district_name.capitalize()}: {location_key}")
        return location_key
