import pytest

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.tests.test_base import test_date
from ontrack.market.models.lookup import Exchange
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)


class TestPullParticipantData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.participant_qs = ParticipantActivity.backend.get_queryset()
        self.participant_stats_qs = ParticipantStatsActivity.backend.get_queryset()

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
        records = result[0]
        assert len(records) > 0
        record_created = result[1][0]
        record_updated = result[1][1]
        assert record_created > 0
        assert record_updated == 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_participant_eod_data(date, True)
        assert result is not None
        records = result[0]
        assert len(records) > 0
        record_created = result[1][0]
        record_updated = result[1][1]
        assert record_created == 0
        assert record_updated > 0

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_stats_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_participant_stats_eod_data(date, True)
        assert result is not None
        records = result[0]
        assert len(records) > 0
        record_created = result[1][0]
        record_updated = result[1][1]
        assert record_created > 0
        assert record_updated == 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_participant_stats_eod_data(date, True)
        assert result is not None
        records = result[0]
        assert len(records) > 0
        record_created = result[1][0]
        record_updated = result[1][1]
        assert record_created == 0
        assert record_updated > 0
