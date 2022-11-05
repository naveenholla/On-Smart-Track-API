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

        exchange_qs = Exchange.backend.get_queryset()
        self.exchange = exchange_qs.unique_search(exchange_symbol).first()

        if not self.exchange:
            return

        equity_qs = Equity.backend.get_queryset()
        self.equity_dict = self.create_dict(equity_qs)

        index_qs = Index.backend.get_queryset()
        self.index_dict = self.create_dict(index_qs, "name")

        self.pull_equity_obj = PullEquityData(self.exchange, self.equity_dict)
        self.pull_index_obj = PullIndexData(self.exchange, self.index_dict)
        self.pull_particpant_obj = PullParticipantData(self.exchange)

    def load_equity_eod_data(self, date):
        already_processed = EquityEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_equity_obj.pull_parse_eod_data(date)

        return result

    def load_equity_derivative_eod_data(self, date):
        already_processed = EquityDerivativeEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_equity_obj.pull_parse_derivative_eod_data(date)

        return result

    def load_index_eod_data(self, date):
        already_processed = IndexEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_index_obj.pull_parse_eod_data(date)

        return result

    def load_index_derivative_eod_data(self, date):
        already_processed = IndexDerivativeEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_index_obj.pull_parse_derivative_eod_data(date)

        return result

    def load_participant_eod_data(self, date):
        already_processed = ParticipantActivity.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_particpant_obj.pull_parse_eod_data(date)

        return result

    def load_participant_stats_eod_data(self, date, save_data=True):
        already_processed = ParticipantStatsActivity.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_particpant_obj.pull_parse_eod_stats(date)

        return result

    def execute_equity_eod_data_task(self, run_date=None, end_date=None):
        output = []
        with application_context(
            exchange=self.exchange,
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.exchange is None:
                return "Exchange is required."

            date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS

            if not run_date:
                cet = self.can_execute_task(date_key, pause_hour_key)
                if not cet[0]:
                    message = cet[1]
                    self.logger.log_info(message)
                    return message
                run_date = cet[2]

            end_date_provided = True
            if not end_date:
                end_date_provided = False
                end_date = dt.current_date_time()

            pause_hours = self.settings.get_by_key(pause_hour_key)
            pause_hours = nh.str_to_float(pause_hours)

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

                try:
                    result = self.load_equity_eod_data(run_date)
                    if isinstance(result, str):
                        output.append(self.message_creator(run_date_str, result))
                    else:
                        with transaction.atomic():
                            records_stats = self.create_or_update(
                                result, EquityEndOfDay
                            )
                            if not end_date_provided:
                                self.settings.save_task_execution_time(
                                    date_key, run_date
                                )

                        output.append(self.message_creator(run_date_str, records_stats))
                except Exception as e:
                    message = f"Exception - `{format(e)}`."
                    self.logger.log_critical(message=message)
                    output.append(self.message_creator(run_date_str, message))

                run_date = dt.get_future_date(run_date, hours=pause_hours)
            return output
