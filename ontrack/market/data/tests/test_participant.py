from datetime import datetime

import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.models.lookup import Exchange
from ontrack.market.models.participant import ParticipantActivity


class TestPullParticipantData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.all()
        self.participant_qs = ParticipantActivity.backend.all()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)

    @pytest.mark.integration
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = datetime(2022, 10, 20)
        result = self.endofdaydata.load_participant_eod_data(date, True)
        assert result is not None

    @pytest.mark.integration
    def test_pull_parse_eod_stats_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = datetime(2022, 10, 20)
        result = self.endofdaydata.load_participant_stats_eod_data(date, True)
        assert result is not None
