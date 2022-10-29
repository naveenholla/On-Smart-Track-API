import pytest
from freezegun import freeze_time

from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.enum import HolidayCategoryType, MarketDayTypeEnum
from ontrack.utils.context import application_context, get_correlation_id
from ontrack.utils.datetime import DateTimeHelper as dt


class TestExchangeData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def exchange_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture

    @pytest.mark.unittest
    def test_exchange_trading_holiday(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            days = dt.get_exchange_trading_holidays()
            assert days is not None
            assert len(days) > 0

    @pytest.mark.unittest
    def test_exchange_is_holiday(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            assert dt.is_holiday(dt.get_date_time(2022, 1, 26))
            assert not dt.is_holiday(dt.get_date_time(2022, 1, 27))
            assert dt.is_holiday(dt.get_date_time(2022, 1, 29))
            assert not dt.is_holiday(dt.get_date_time(2022, 10, 24))

    @pytest.mark.unittest
    def test_exchange_start_time(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            date = dt.get_date_time(2022, 10, 20, 9, 15, 0)
            result = dt.get_market_start_time(date)
            assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 24, 18, 15, 0)
            result = dt.get_market_start_time(date)
            assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 20, 9, 15, 0)
            with freeze_time(date):
                result = dt.get_market_start_time()
                assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 24, 18, 15, 0)
            with freeze_time(date):
                result = dt.get_market_start_time()
                assert dt.compare_date_time(result, date)

    @pytest.mark.unittest
    def test_exchange_end_time(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            date = dt.get_date_time(2022, 10, 20, 15, 30, 0)
            result = dt.get_market_end_time(date)
            assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 24, 19, 15, 0)
            result = dt.get_market_end_time(date)
            assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 20, 15, 30, 0)
            with freeze_time(date):
                result = dt.get_market_end_time()
                assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 24, 19, 15, 0)
            with freeze_time(date):
                result = dt.get_market_end_time()
                assert dt.compare_date_time(result, date)

    @pytest.mark.unittest
    def test_exchange_refresh_time(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            date = dt.get_date_time(2022, 10, 20, 20, 00, 0)
            result = dt.get_market_refresh_time(date)
            assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 20, 20, 00, 0)
            with freeze_time(date):
                result = dt.get_market_refresh_time()
                assert dt.compare_date_time(result, date)

            date = dt.get_date_time(2022, 10, 20, 21, 00, 0)
            with freeze_time(date):
                assert dt.is_data_refreshed()

    @pytest.mark.unittest
    def test_is_market_open(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            date = dt.get_date_time(2022, 10, 20, 21, 0, 0)
            with freeze_time(date):
                assert not dt.is_market_open()

            date = dt.get_date_time(2022, 10, 20, 10, 0, 0)
            with freeze_time(date):
                assert dt.is_market_open()

            date = dt.get_date_time(2022, 10, 20, 8, 0, 0)
            with freeze_time(date):
                assert not dt.is_market_open()

            date = dt.get_date_time(2022, 10, 20, 9, 15, 1)
            with freeze_time(date):
                assert dt.is_market_open()

    @pytest.mark.unittest
    def test_is_market_close_for_the_day(self):
        correlationid = get_correlation_id()
        with application_context(
            correlationid=correlationid,
            exchange=self.exchange_fixture,
            holiday_category_name=HolidayCategoryType.EQUITIES,
            holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
        ):
            date = dt.get_date_time(2022, 1, 26, 10, 0, 0)
            with freeze_time(date):
                assert dt.is_market_close_for_the_day()

            date = dt.get_date_time(2022, 10, 20, 10, 0, 0)
            with freeze_time(date):
                assert not dt.is_market_close_for_the_day()

            date = dt.get_date_time(2022, 10, 20, 8, 0, 0)
            with freeze_time(date):
                assert not dt.is_market_close_for_the_day()

            date = dt.get_date_time(2022, 10, 20, 16, 15, 1)
            with freeze_time(date):
                assert dt.is_market_close_for_the_day()
