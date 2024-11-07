from abc import ABC, abstractmethod
from typing import Union
import requests
from Utils import *
from UnicodeTR import UnicodeTR


class VegetationCollector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, district: AnyStr):
        raise NotImplementedError("You need to implement get_pollen_data function.")

    @abstractmethod
    def save(self, data: Union[List[Dict], Dict], filename: AnyStr):
        raise NotImplementedError("You need to implement save function.")


class PlantNet(VegetationCollector):
    def __init__(self):
        super().__init__()
        self.occurrence_url = "https://api.gbif.org/v1/occurrence/search"

    def get_data(self, district: AnyStr):
        district = UnicodeTR(district.strip()).capitalize()
        city_name = get_city_name(district)
        coordinates = get_lat_long(district, city_name)

        polygon: str = f"POLYGON(({coordinates['southwest_lon']} {coordinates['southwest_lat']}, " \
                       f"{coordinates['southwest_lon']} {coordinates['northeast_lat']}, " \
                       f"{coordinates['northeast_lon']} {coordinates['northeast_lat']}, " \
                       f"{coordinates['northeast_lon']} {coordinates['southwest_lat']}, " \
                       f"{coordinates['southwest_lon']} {coordinates['southwest_lat']}))"
        params = {
            "geometry": polygon
        }

        response = requests.get(self.occurrence_url, params=params)
        data = response.json()

        for record in data.get("results", []):
            print({
                "scientificName": record.get("scientificName"),
                "latitude": record.get("decimalLatitude"),
                "longitude": record.get("decimalLongitude"),
                "eventDate": record.get("eventDate"),
                "media": [media.get("identifier") for media in record.get("media", [])]
            })

        pass

    def save(self, data: Union[List[Dict], Dict], filename: AnyStr):
        pass

#https://identify.plantnet.org/tr/prediction?polygon={"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[27.231456,37.820097],[27.231456,37.880279],[27.309491,37.880279],[27.309491,37.820097],[27.231456,37.820097]]]}}
