from sqlalchemy import create_engine
import json
from typing import Union, List, Dict, AnyStr
import pandas as pd
from datetime import datetime
from Utils import fahrenheit_to_celsius, mph_to_kph, inch_to_millimeter


class DatabaseHandler:
    def __init__(self, config_path: str, table_name: str, redundant_columns: List[AnyStr], fahrenheit_unit_columns: List[AnyStr],
                 mph_unit_columns: List[AnyStr], in_unit_columns: List[AnyStr]):
        with open(config_path, "r") as configurations:
            __configurations = json.load(configurations)

        self.engine = create_engine(
            f"postgresql://{__configurations['db_user']}:{__configurations['db_password']}@{__configurations['db_host']}:{__configurations['db_port']}/{__configurations['db_name']}"
        )
        self.table_name = table_name

        self.__redundant_columns = redundant_columns
        self.__fahrenheit_unit_columns = fahrenheit_unit_columns
        self.__mph_unit_columns = mph_unit_columns
        self.__in_unit_columns = in_unit_columns

    def save_to_database(self, data: Union[List[Dict], Dict]):
        if isinstance(data, dict):
            data = [data]
        normalized_daily_dataframes = []

        for day_data in data:
            normalized_dataframe = pd.json_normalize(day_data, sep="_")

            if "AirAndPollen" in normalized_dataframe.columns:
                air_and_pollen = normalized_dataframe["AirAndPollen"].apply(pd.Series)
                air_and_pollen.columns = [f"AirAndPollen_{item["Name"]}" for item in air_and_pollen.iloc[0]]

                for column in air_and_pollen.columns:
                    air_and_pollen[column] = air_and_pollen[column].apply(lambda x: x['Category'] if isinstance(x, dict) else x)

                normalized_dataframe = pd.concat([normalized_dataframe.drop(columns=["AirAndPollen"]), air_and_pollen], axis=1)

            normalized_dataframe["Date"] = datetime.now()
            normalized_daily_dataframes.append(normalized_dataframe)

        result_dataframe = pd.concat(normalized_daily_dataframes, ignore_index=True)
        result_dataframe = self.__preprocess_columns(result_dataframe)

        result_dataframe.to_sql(self.table_name, self.engine, if_exists="append", index=False)
        print(f"{len(result_dataframe)} rows added to {self.table_name} database table.")

    def __preprocess_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe.drop(columns=[column for column in dataframe.columns if "Unit" in column], inplace=True)
        dataframe.drop(columns=self.__redundant_columns, inplace=True, errors='ignore')

        for col in self.__fahrenheit_unit_columns:
            if col in dataframe.columns:
                dataframe[col] = dataframe[col].apply(fahrenheit_to_celsius)

        for col in self.__mph_unit_columns:
            if col in dataframe.columns:
                dataframe[col] = dataframe[col].apply(mph_to_kph)

        for col in self.__in_unit_columns:
            if col in dataframe.columns:
                dataframe[col] = dataframe[col].apply(inch_to_millimeter)

        return dataframe
