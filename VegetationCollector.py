from abc import ABC, abstractmethod
from typing import Union, List, Dict
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


class VegetationCollector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, district: str):
        raise NotImplementedError("You need to implement get_pollen_data function.")

    @abstractmethod
    def save(self, data: Union[List[Dict], Dict], filename: str):
        raise NotImplementedError("You need to implement save function.")

class PlantNet(VegetationCollector):
    def __init__(self):
        super().__init__()
        self.geo_app_url = "https://identify.plantnet.org/tr/prediction"


    def get_data(self, district: str):
        pass

    def save(self, data: Union[List[Dict], Dict], filename: str):
        pass


#https://identify.plantnet.org/tr/prediction?polygon={"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[27.231456,37.820097],[27.231456,37.880279],[27.309491,37.880279],[27.309491,37.820097],[27.231456,37.820097]]]}}