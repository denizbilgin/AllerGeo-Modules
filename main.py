from WeatherDataCollector import *
from Utils import *
import pandas as pd
from VegetationCollector import *
from UnicodeTR import UnicodeTR


if __name__ == '__main__':
    pollen_data_collector = AccuWeather()
    vegetation_collector = PlantNet()
    pollen_data_collector.save_aegean("aegean_weather_data.csv")

    #district_name = "Ula"
    #district_name = UnicodeTR(district_name).capitalize()
    #parent_name = get_city_name(district_name)
    #print(district_name, "-", parent_name)
    #species = vegetation_collector.get_data(district_name)
    #for individual_species in species:
    #    print(individual_species)
    #    print()


