from WeatherDataCollector import *
from Utils import *
import pandas as pd


if __name__ == '__main__':
    pollen_data_collector = AccuWeather()
    pollen_data_collector.save_aegean("aegean_weather_data.csv")

    #district_name = "Çay"
    #city_name = get_city_name(district_name)
    #lat, long = get_lat_long(district_name, city_name)
    #print(f"Latitude and Longitude of {district_name}: {lat} - {long}")
