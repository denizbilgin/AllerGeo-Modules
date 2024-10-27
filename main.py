from WeatherDataCollector import *


if __name__ == '__main__':
    pollen_data_collector = WeatherCollectorSelenium()
    results = pollen_data_collector.get_data("Muğla", "2024-10-25")
    pollen_data_collector.save(results, "weather_data.csv")
