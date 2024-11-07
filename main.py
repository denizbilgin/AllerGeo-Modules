from WeatherDataCollector import *
from Utils import *
import pandas as pd


if __name__ == '__main__':
    pollen_data_collector = AccuWeather()
    pollen_data_collector.save_aegean("aegean_weather_data.csv")

    #district_name = "Söğüt"
    #similar_name = find_similar_place(district_name)
    #print(f"Similar name of {district_name} is: {similar_name}")
    #city_name = get_city_name(district_name)
    #data = get_lat_long(district_name, city_name)
    #print(f"Latitude and Longitude of {district_name}: {data}")
