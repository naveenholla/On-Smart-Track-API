from unittest.mock import MagicMock, patch

import pytest

from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.lookup import EquityIndex, Exchange
from ontrack.utils.base.enum import AdminSettingKey, ExchangeType
from ontrack.utils.datetime import DateTimeHelper as dt


class TestLogicLookup:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def exchange_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture

    @pytest.mark.unittest
    def test_execute_market_lookup_data_task(self):
        obj = MarketLookupData("None")
        obj.load_equity_data = MagicMock(return_value=(None, (1, 0)))
        obj.load_index_data = MagicMock(return_value=(None, (1, 0)))
        obj.load_equity_index_data = MagicMock(return_value=(None, (1, 0)))
        obj.settings.save_task_execution_time = MagicMock()
        obj.settings.can_execute_task = MagicMock(
            return_value=(False, dt.current_date_time())
        )

        obj.execute_market_lookup_data_task()

        obj.load_equity_data.assert_not_called()
        obj.load_index_data.assert_not_called()
        obj.load_equity_index_data.assert_not_called()

        with patch.object(EquityIndex.backend, "delete_old_records", return_value=None):
            obj.settings.can_execute_task = MagicMock(
                return_value=(True, dt.current_date_time())
            )

            obj.execute_market_lookup_data_task()

            obj.load_equity_data.assert_called()
            obj.load_index_data.assert_called()
            obj.load_equity_index_data.assert_called()
            obj.settings.save_task_execution_time.assert_called_with(
                AdminSettingKey.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
            )

    @pytest.mark.unittest
    def test_execute_market_lookup_data_task_2(self):
        obj = MarketLookupData(ExchangeType.NSE)
        obj.load_equity_data = MagicMock(return_value=None)
        obj.load_index_data = MagicMock(return_value=None)
        obj.load_equity_index_data = MagicMock(return_value=None)
        result = obj.execute_market_lookup_data_task()
        assert result is not None

    @pytest.mark.unittest
    def test_execute_holidays_lookup_data_task(self):
        obj = MarketLookupData("None")
        obj.load_holidays_data = MagicMock(return_value=None)
        obj.settings.save_task_execution_time = MagicMock()
        obj.settings.can_execute_task = MagicMock(
            return_value=(False, dt.current_date_time())
        )

        obj.execute_holidays_lookup_data_task()

        obj.load_holidays_data.assert_not_called()

        with patch.object(EquityIndex.backend, "delete_old_records", return_value=None):
            obj.settings.can_execute_task = MagicMock(
                return_value=(True, dt.current_date_time())
            )

            obj.execute_holidays_lookup_data_task()

            obj.load_holidays_data.assert_called()
            obj.settings.save_task_execution_time.assert_called_with(
                AdminSettingKey.DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE
            )
