import json
from functools import lru_cache

import pandas as pd
from django.conf import settings

from ontrack.utils.logger import ApplicationLogger


class Configurations:
    logger = ApplicationLogger()

    @staticmethod
    def __get_config(fileName: str):
        path = f"{str(settings.CONFIG_DIR)}/{fileName}.json"
        Configurations.logger.log_debug(f"Reading configuration [{path}].")

        # read all the file content
        with open(path) as config:
            jsonServerData = json.load(config)
            return jsonServerData

    @staticmethod
    def set_config(fileName: str, content):
        df = pd.DataFrame(content)
        path = f"{str(settings.CONFIG_DIR)}/{fileName}.json"

        Configurations.logger.log_debug(f"Saving configuration [{path}].")
        df.to_json(path, orient="records", compression="infer", index="true")

    @staticmethod
    def clear_cache():
        Configurations.get_urls_config.cache_clear()
        Configurations.get_default_values_config.cache_clear()

    @staticmethod
    @lru_cache(1)
    def get_urls_config():
        return Configurations.__get_config("urlconfig")

    @staticmethod
    @lru_cache(1)
    def get_default_values_config():
        return Configurations.__get_config("default_values")

    @staticmethod
    def get_default_value_by_key(key):
        return Configurations.get_default_values_config()[key]

    @staticmethod
    @lru_cache(1)
    def get_header_values_config():
        return Configurations.__get_config("header_values")
