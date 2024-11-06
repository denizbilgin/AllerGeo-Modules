from abc import ABC, abstractmethod
from typing import Union, List, Dict


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
    def get_data(self, district: str):
        pass

    def save(self, data: Union[List[Dict], Dict], filename: str):
        pass