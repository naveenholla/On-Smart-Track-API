import os
import zipfile

import requests
from django.conf import settings

from .logger import ApplicationLogger


class FileSystemHelper:
    logger = ApplicationLogger()

    @staticmethod
    def create_temp_folder(folder_name, temp_folder_path=None):
        if temp_folder_path is None:
            temp_folder_path = settings.TEMP_DIR

        # temp folder to store files
        fixtures_dir = temp_folder_path / folder_name
        if not os.path.exists(fixtures_dir):
            fixtures_dir.mkdir()
        return fixtures_dir

    @staticmethod
    def download_extract_zip(url, folder_path, skip_if_exists=True):
        # importing necessary modules

        file_name = url.split("/")[-1].replace(".zip", "")

        from os.path import exists

        if skip_if_exists and exists(folder_path / file_name):
            return file_name

        from io import BytesIO

        FileSystemHelper.logger.log_debug(f"Downloading started {url}")

        # Downloading the file by sending the request to the URL
        req = requests.get(url)

        FileSystemHelper.logger.log_debug("Downloading Completed")

        # extracting the zip file contents
        zipfile_bytes = zipfile.ZipFile(BytesIO(req.content))
        zipfile_bytes.extractall(folder_path)

        return file_name
