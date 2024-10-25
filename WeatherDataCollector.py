from abc import ABC, abstractmethod
import requests
from datetime import datetime, timedelta
from typing import List, Dict


class WeatherDataCollector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, district: str, date: str, date_range: int = 4) -> List[Dict]:
        raise NotImplementedError("You need to implement get_pollen_data function.")


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
        daily_pollen_data = []

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
                    date_pollen_data = {'date': date.strftime("%Y-%m-%d"), 'pollen': []}

                    if 'AirAndPollen' in forecast:
                        for pollen_dict in forecast['AirAndPollen']:
                            date_pollen_data["pollen"].append({
                                "name": pollen_dict['Name'],
                                "level": pollen_dict['Value'],
                                "category": pollen_dict["Category"]
                            })
                    daily_pollen_data.append(date_pollen_data)
            else:
                raise Exception(f"Could not get data for {formatted_date}. Status Code: {response.status_code}")

        return daily_pollen_data

    def __get_location_key(self, district_name: str) -> str:
        location_url = f"https://dataservice.accuweather.com/locations/v1/cities/search"
        params = {
            'apikey': self.API_KEY,
            'q': district_name
        }
        location_data = requests.get(location_url, params=params).json()
        location_key = location_data[0]['Key']
        print(f"Location Key for {district_name.capitalize()}: {location_key}")
        print(type(location_key))
        return location_key
