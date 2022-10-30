from django.conf import settings
from django.core.management import call_command

from ontrack.utils.filesystem import FileSystemHelper
from ontrack.utils.logger import ApplicationLogger


class FixtureData:
    def __init__(self):
        self.logger = ApplicationLogger()

    def __load_fixture_data(self, fixture, temp_folder_path=None):
        temp_folder = FileSystemHelper.create_temp_folder("fixtures", temp_folder_path)
        app_folder = settings.APPS_FOLDER_NAME

        fixture_details = fixture.split(".")
        app_name = fixture_details[0]
        model = fixture_details[1]
        source = f"{app_folder}/{app_name}/fixtures/{model}.json"
        destination = temp_folder / f"{model}.json"

        with open(source, "rb") as f:
            data = f.read()

        with open(destination, "wb") as f_new:
            f_new.write(data)

        call_command("loaddata", destination)

    def load_fixtures_data(self, fixtures, temp_folder_path=None):
        for fixture in fixtures:
            self.__load_fixture_data(fixture, temp_folder_path)
