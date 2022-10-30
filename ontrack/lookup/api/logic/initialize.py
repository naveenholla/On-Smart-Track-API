from ontrack.utils.base.fixtures import FixtureData
from ontrack.utils.logger import ApplicationLogger


class InitializeData:
    def __init__(self):
        self.logger = ApplicationLogger()
        self.fixtureData = FixtureData()

    def load_fixtures_all_data(self, temp_folder_path=None):
        fixtures = [
            "lookup.setting",
        ]

        self.fixtureData.load_fixtures_data(fixtures, temp_folder_path)
