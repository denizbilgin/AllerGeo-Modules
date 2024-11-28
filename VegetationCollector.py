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
        self.species_url = "https://api.gbif.org/v1/species"

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

        occurrences = []
        for record in data.get("results", []):

            occurrences.append({
                "scientific_name": record.get("acceptedScientificName"),
                "species_name": record.get("species"),
                "accepted_taxon_key": record.get("acceptedTaxonKey"),
                "common_names": self.get_species_common_name(record.get("acceptedTaxonKey")),
                "latitude": record.get("decimalLatitude"),
                "longitude": record.get("decimalLongitude"),
                "basis_of_record": record.get("basisOfRecord"),
                "date_identified": record.get("dateIdentified"),
                "media": [media.get("identifier") for media in record.get("media", [])]
            })
        return occurrences

    def get_species_common_name(self, taxon_key: int) -> Dict[AnyStr, AnyStr]:
        response = requests.get(f"{self.species_url}/{str(taxon_key)}/vernacularNames")
        if response.status_code == 200:
            data = response.json()["results"]
            result_dict: Dict[AnyStr, AnyStr] = {}
            for common_name in data:
                result_dict[common_name["language"]] = common_name["vernacularName"]
            result_dict["tr"] = translate_to_turkish(result_dict)
            return result_dict
        else:
            print(f"API request failed with status code {response.status_code}")
            return {"error": "Failed to retrieve data."}

    def save(self, data: Union[List[Dict], Dict], filename: AnyStr):
        pass
