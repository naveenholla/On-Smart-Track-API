import os

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
