from WeatherDataCollector import *
from Utils import *


if __name__ == '__main__':
    pollen_data_collector = AccuWeather()
    pollen_data_collector.save_aegean("aegean_weather_data.csv")