import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.tests.test_base import test_date
from ontrack.market.models.lookup import Exchange
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)


class TestPullParticipantData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.all()
        self.participant_qs = ParticipantActivity.backend.all()
        self.participant_stats_qs = ParticipantStatsActivity.backend.all()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_participant_eod_data(date, True)
        assert result is not None

        records_count = self.participant_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_participant_eod_data(date, True)
        assert result is not None
        assert records_count == self.participant_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_stats_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_participant_stats_eod_data(date, True)
        assert result is not None

        records_count = self.participant_stats_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_participant_stats_eod_data(date, True)
        assert result is not None
        assert records_count == self.participant_stats_qs.all().count()
