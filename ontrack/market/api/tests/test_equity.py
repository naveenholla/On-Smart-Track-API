from unittest.mock import MagicMock, patch

import pytest

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.logic.livedata import LiveData
from ontrack.market.api.logic.lookup import InitializeData
from ontrack.market.api.tests.test_base import (
    assert_record_creation,
    assert_record_updation,
    test_date,
)
from ontrack.market.models.equity import (
    EquityDerivativeEndOfDay,
    EquityEndOfDay,
    EquityLiveData,
    EquityLiveDerivativeData,
    EquityLiveOpenInterest,
    EquityLiveOptionChain,
)
from ontrack.market.models.lookup import Equity, EquityIndex, Exchange
from ontrack.utils.base.enum import AdminSettingKey
from ontrack.utils.config import Configurations


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.equity_qs = Equity.backend.get_queryset()
        self.equity_eod_qs = EquityEndOfDay.backend.get_queryset()
        self.equity_derivative_eod_qs = EquityDerivativeEndOfDay.backend.get_queryset()
        self.equity_live_data_qs = EquityLiveData.backend.get_queryset()
        self.equity_live_open_interest_qs = (
            EquityLiveOpenInterest.backend.get_queryset()
        )
        self.equity_live_derivative_qs = EquityLiveDerivativeData.backend.get_queryset()
        self.equity_live_option_chain_qs = EquityLiveOptionChain.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.initializeData = InitializeData(exchange_fixture.symbol)

        self.initializeData.load_equity_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)
        self.livedata = LiveData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.initializeData.load_equity_data(True)
        assert result is not None
        records = result[0]
        assert len(records) > 0

        stocks_with_lot_size = [x for x in records if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in records if x["symbol"] == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        equity_fixture = self.equity_qs.unique_search(symbol="reliance").first()
        assert equity_fixture is not None and equity_fixture.id is not None
        symbol = equity_fixture.symbol
        stock2 = [x for x in records if x["symbol"] == symbol][0]
        assert stock2["id"] == equity_fixture.id

        # check update logic
        result = self.initializeData.load_equity_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert_record_creation(result)

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_derivative_eod_data(date, True)
        assert_record_creation(result)

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_derivative_eod_data(date, True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_equity_live_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_open_interest_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_open_interest_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_equity_live_open_interest_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_derivative_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_derivative_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_equity_live_derivative_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_option_chain_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_option_chain_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_equity_live_option_chain_data(True)
        assert_record_updation(result)

    @pytest.mark.unittest
    def test_execute_equity_lookup_data_task(self):
        obj = InitializeData("None")
        obj.load_equity_data = MagicMock(return_value=(None, (1, 0)))
        obj.load_index_data = MagicMock(return_value=(None, (1, 0)))
        obj.load_equity_index_data = MagicMock(return_value=(None, (1, 0)))
        obj.settings.save_task_execution_time = MagicMock()
        EquityIndex.backend.delete_old_records = MagicMock()
        Configurations.get_default_value_by_key = MagicMock(return_value=2000)

        with patch.object(SettingLogic, "can_execute_task", return_value=False):
            obj.execute_equity_lookup_data_task()
            obj.load_equity_data.assert_not_called()
            obj.load_index_data.assert_not_called()
            obj.load_equity_index_data.assert_not_called()

        with patch.object(SettingLogic, "can_execute_task", return_value=True):
            obj.execute_equity_lookup_data_task()
            obj.load_equity_data.assert_called()
            obj.load_index_data.assert_called()
            obj.load_equity_index_data.assert_called()
            EquityIndex.backend.delete_old_records.assert_called_with(2000)
            obj.settings.save_task_execution_time.assert_called_with(
                AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DATE
            )
