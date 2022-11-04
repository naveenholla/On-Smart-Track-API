from django.db import transaction

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.participant import PullParticipantData
from ontrack.market.models.equity import EquityDerivativeEndOfDay, EquityEndOfDay
from ontrack.market.models.index import IndexDerivativeEndOfDay, IndexEndOfDay
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)
from ontrack.utils.base.enum import AdminSettingKey as sk
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper as nh


class EndOfDayData(BaseLogic):
    def __init__(self, exchange_symbol: str):
        self.logger = ApplicationLogger()
        self.settings = SettingLogic()

        self.exchange_symbol = exchange_symbol

        self.exchange_qs = Exchange.backend.get_queryset()
        self.equity_qs = Equity.backend.get_queryset()

        self.index_qs = Index.backend.get_queryset()
        self.exchange_qs = Exchange.backend.get_queryset()

        self.equity_eod_qs = EquityEndOfDay.backend.get_queryset()
        self.index_eod_qs = IndexEndOfDay.backend.get_queryset()

        self.equity_derivative_eod_qs = EquityDerivativeEndOfDay.backend.get_queryset()
        self.index_derivative_eod_qs = IndexDerivativeEndOfDay.backend.get_queryset()

        self.participant_qs = ParticipantActivity.backend.get_queryset()
        self.participant_stats_qs = ParticipantStatsActivity.backend.get_queryset()

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()

    def load_equity_eod_data(self, date, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol, self.exchange_qs, self.equity_qs, self.equity_eod_qs
        )

        result = pull_equity_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.create_or_update(result, EquityEndOfDay)

        return result, records_stats

    def load_equity_derivative_eod_data(self, date, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
            self.equity_eod_qs,
            self.equity_derivative_eod_qs,
        )

        result = pull_equity_obj.pull_parse_derivative_eod_data(date)
        if save_data:
            records_stats = self.create_or_update(result, EquityDerivativeEndOfDay)

        return result, records_stats

    def load_index_eod_data(self, date, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol, self.exchange_qs, self.index_qs, self.index_eod_qs
        )

        result = pull_index_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.create_or_update(result, IndexEndOfDay)

        return result, records_stats

    def load_index_derivative_eod_data(self, date, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
            self.index_eod_qs,
            self.index_derivative_eod_qs,
        )

        result = pull_index_obj.pull_parse_derivative_eod_data(date)
        if save_data:
            records_stats = self.create_or_update(result, IndexDerivativeEndOfDay)

        return result, records_stats

    def load_participant_eod_data(self, date, save_data=True):
        pull_particpant_obj = PullParticipantData(
            self.exchange_symbol,
            self.exchange_qs,
            self.participant_qs,
        )

        result = pull_particpant_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.create_or_update(result, ParticipantActivity)

        return result, records_stats

    def load_participant_stats_eod_data(self, date, save_data=True):
        pull_particpant_obj = PullParticipantData(
            self.exchange_symbol,
            self.exchange_qs,
            self.participant_qs,
            self.participant_stats_qs,
        )

        result = pull_particpant_obj.pull_parse_eod_stats(date)
        if save_data:
            records_stats = self.create_or_update(result, ParticipantStatsActivity)

        return result, records_stats

    def load_eod_data(self, date):
        self.load_equity_eod_data(date)
        self.load_index_eod_data(date)

        self.load_equity_derivative_eod_data(date)
        self.load_index_derivative_eod_data(date)

        self.load_participant_eod_data(date)

    def execute_equity_eod_data_task(self):
        output = []
        with application_context(
            exchange=self.exchange,
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.exchange is None:
                return "Exchange is required."

            date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS
            default_value_key = sk.DEFAULT_START_DATE_EQUITY_DATA_PULL
            end_date_key = sk.DEFAULT_END_DATE_EQUITY_DATA_PULL

            cet = self.can_execute_task(date_key, pause_hour_key, default_value_key)
            if not cet[0]:
                message = cet[1]
                self.logger.log_info(message)
                return message

            pause_hours = self.settings.get_by_key(pause_hour_key)
            pause_hours = nh.str_to_float(pause_hours)
            end_date_config = self.settings.get_by_key(end_date_key)

            run_date = cet[2]
            end_date = dt.current_date_time()
            if end_date_config is not None:
                end_date = dt.str_to_datetime(end_date_config)

            self.logger.log_debug(f"End Date:{end_date}")
            self.logger.log_debug(f"Date:{run_date}")

            while dt.compare_date_time(run_date, end_date, "lte"):
                self.logger.log_debug(f"Processing Date:{run_date}")
                run_date_str = dt.datetime_to_display_str(run_date)

                if dt.is_holiday(run_date):
                    self.settings.save_task_execution_time(date_key, run_date)
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "It a is holiday."
                    output.append(self.message_creator(run_date_str, message))
                    self.logger.log_info(message)
                    continue

                if not dt.is_data_refreshed(run_date, end_date):
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "Data is not refreshed yet."
                    output.append(self.message_creator(run_date_str, message))
                    self.logger.log_info(message)
                    continue

                with transaction.atomic():
                    result = self.load_equity_eod_data(run_date)
                    self.settings.save_task_execution_time(date_key, run_date)

                output.append(self.message_creator(run_date_str, result))

                run_date = dt.get_future_date(run_date, hours=pause_hours)

            if end_date_config is not None:
                self.settings.save_setting(end_date_key, None)

            return output
