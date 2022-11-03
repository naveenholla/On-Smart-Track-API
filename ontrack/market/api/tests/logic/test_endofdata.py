from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.enum import ExchangeType
from ontrack.utils.datetime import DateTimeHelper as dt


class TestLogicLookup:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def exchange_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture

    @pytest.mark.unittest
    def test_execute_market_lookup_data_task_2(self):
        obj = EndOfDayData(ExchangeType.NSE)
        obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
        result = obj.execute_equity_eod_data_task()
        assert result is not None

    @pytest.mark.unittest
    def test_execute_market_lookup_data_task_Exchange_None(self):
        obj = EndOfDayData("Not-Existing-Exchange")
        obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
        result = obj.execute_equity_eod_data_task()
        assert result is not None

    @pytest.mark.unittest
    def test_execute_market_lookup_data_task_Date_1(self):
        last_excution_date = dt.get_date_time(2022, 10, 10, 15, 30, 0)
        current_date = dt.get_date_time(2022, 10, 18, 15, 30, 0)

        with freeze_time(current_date):
            obj = EndOfDayData(ExchangeType.NSE)
            obj.can_execute_task = MagicMock(
                return_value=(True, None, last_excution_date)
            )
            obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
            result = obj.execute_equity_eod_data_task()
            assert result is not None
