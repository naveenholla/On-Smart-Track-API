from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.enum import AdminSettingKey as sk
from ontrack.utils.base.enum import ExchangeType
from ontrack.utils.datetime import DateTimeHelper as dt


class TestLogicLookup:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def exchange_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.settings = SettingLogic()

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
        last_excution_date = dt.get_date_time(2022, 10, 19, 0, 0, 0)
        current_date = dt.get_date_time(2022, 10, 27, 15, 30, 0)
        end_date = dt.datetime_to_str(dt.get_date_time(2022, 10, 20, 15, 30, 0))
        end_date_key = sk.DEFAULT_END_DATE_EQUITY_DATA_PULL

        with freeze_time(current_date):
            self.settings.save_setting(end_date_key, end_date)

            obj = EndOfDayData(ExchangeType.NSE)
            obj.can_execute_task = MagicMock(
                return_value=(True, None, last_excution_date)
            )
            obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
            result = obj.execute_equity_eod_data_task()
            assert result is not None
            assert len(result) == 2
            assert "message" in result[1]
            assert obj.load_equity_eod_data.call_count == 1

            obj = EndOfDayData(ExchangeType.NSE)
            obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
            result = obj.execute_equity_eod_data_task()
            assert result is not None
            assert len(result) == 8
            assert "message" in result[2]
            assert "message" in result[3]
            assert "message" in result[6]
            assert "message" in result[7]
            assert obj.load_equity_eod_data.call_count == 4

            obj = EndOfDayData(ExchangeType.NSE)
            obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
            result = obj.execute_equity_eod_data_task()
            assert result is not None
            assert len(result) == 1
            assert "message" in result[0]
            obj.load_equity_eod_data.assert_not_called()

        current_date = dt.get_date_time(2022, 10, 27, 22, 15, 0)
        with freeze_time(current_date):
            obj = EndOfDayData(ExchangeType.NSE)
            obj.load_equity_eod_data = MagicMock(return_value=(None, (1, 0)))
            result = obj.execute_equity_eod_data_task()
            assert result is not None
            assert len(result) == 1
            assert obj.load_equity_eod_data.call_count == 1
