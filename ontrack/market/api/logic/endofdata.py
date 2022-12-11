from django.db import transaction

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.participant import PullParticipantData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.equity import EquityDerivativeEndOfDay, EquityEndOfDay
from ontrack.market.models.index import IndexDerivativeEndOfDay, IndexEndOfDay
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)
from ontrack.utils.base.enum import AdminSettingKey as sk
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.numbers import NumberHelper as nh


class EndOfDayData(BaseLogic):
    def __init__(self, exchange_symbol: str, recorder=None):
        self.settings = SettingLogic()
        self.marketlookupdata = MarketLookupData(exchange_symbol)

        tp = TaskProgressStatus(recorder)
        self.tp = tp

        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        inx = self.marketlookupdata.index_dict()

        self.pull_equity_obj = PullEquityData(ex, eq, tp)
        self.pull_index_obj = PullIndexData(ex, inx, tp)
        self.pull_participant_obj = PullParticipantData(ex, tp)

    def load_equity_eod_data(self, date):
        already_processed = EquityEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_equity_obj.pull_parse_eod_data(date)

        return result

    def load_equity_corporate_action(self, date):
        result = self.pull_equity_obj.pull_parse_corporate_action(date)
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

        result = self.pull_participant_obj.pull_parse_eod_data(date)

        return result

    def load_participant_stats_eod_data(self, date, save_data=True):
        already_processed = ParticipantStatsActivity.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_participant_obj.pull_parse_eod_stats(date)

        return result

    def __update_company_action(self, results):
        if results is None:
            return

        for action in results:
            subject = action["subject"]
            symbol = action["symbol"]
            exDate = action["exDate"]
            entry_type = action["entry_type"]
            values = action["values"]

            multiplier = 0
            if entry_type == "bonus":
                multiplier = values[0] + values[1]
            elif entry_type == "split":
                multiplier = values[0] / values[1]
            else:
                continue

            self.tp.log_message(f"{symbol} - {exDate} - {entry_type} - {subject}")
            self.tp.log_message(f"Multiplier: {multiplier}")

            updated_records = []
            records = EquityEndOfDay.backend.filter(
                entity__symbol__iexact=symbol, date__lt=exDate
            )
            record_exdate = EquityEndOfDay.backend.filter(
                entity__symbol__iexact=symbol, date=exDate
            ).first()

            if record_exdate:
                close = float(record_exdate.close_price)
                preclose = float(record_exdate.prev_close) / multiplier
                pointchanged = close - preclose
                record_exdate.prev_close = nh.round_to_market_Price(preclose)
                record_exdate.point_changed = nh.round_to_market_Price(pointchanged)
                record_exdate.percentage_changed = nh.round_to_market_Price(
                    pointchanged / close * 100
                )
                updated_records.append(record_exdate)

            for record in records:
                price = float(record.prev_close)
                converted = nh.round_to_market_Price(price / multiplier)
                record.prev_close = converted

                price = float(record.open_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.open_price = converted

                price = float(record.high_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.high_price = converted

                price = float(record.low_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.low_price = converted

                price = float(record.last_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.last_price = converted

                price = float(record.close_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.close_price = converted

                price = float(record.avg_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.avg_price = converted

                price = float(record.point_changed)
                converted = nh.round_to_market_Price(price / multiplier)
                record.point_changed = converted

                price = float(record.traded_quantity)
                converted = nh.round_to_market_Price(price * multiplier)
                record.traded_quantity = converted

                price = float(record.delivery_quantity)
                converted = nh.round_to_market_Price(price * multiplier)
                record.delivery_quantity = converted

                price = record.traded_quantity / float(record.number_of_trades)
                record.quantity_per_trade = price

                updated_records.append(record)

            EquityEndOfDay.backend.bulk_update(
                updated_records,
                [
                    "prev_close",
                    "open_price",
                    "high_price",
                    "low_price",
                    "last_price",
                    "close_price",
                    "avg_price",
                    "point_changed",
                    "percentage_changed",
                    "traded_quantity",
                    "quantity_per_trade",
                    "delivery_quantity",
                ],
            )

            self.tp.log_message(f"Updated: {len(updated_records)}")

    def __save_record(self, result, modeltype, title):
        records_stats = self.create_or_update(result, modeltype)
        stats = self.message_creator(f"{title}", records_stats)
        self.tp.log_records_stats(stats, f"{title} - Stats")
        return stats

    def __execute_eod_data_task(
        self,
        run_date,
        end_date,
        date_key,
        pause_hour_key,
        default_start_key,
        execute_method,
    ):

        self.output = []
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.marketlookupdata.exchange() is None:
                self.tp.log_error("Exchange is required.")
                return "Exchange is required."

            if not run_date:
                cet = self.can_execute_task(date_key, pause_hour_key, default_start_key)
                if not cet[0]:
                    message = cet[1]
                    self.output.append(self.message_creator("EOD", message))
                    self.tp.log_completed(message)
                    return self.output
                run_date = cet[2]

            end_date_provided = True
            if not end_date:
                end_date_provided = False
                end_date = dt.current_date_time()

            pause_hours = self.settings.get_by_key(pause_hour_key)
            pause_hours = nh.str_to_float(pause_hours)

            self.tp.log_debug(f"End Date:{end_date}")
            self.tp.log_debug(f"Date:{run_date}")

            while dt.compare_date_time(run_date, end_date, "lte"):
                self.tp.log_debug(f"Processing Date:{run_date}")
                run_date_str = dt.datetime_to_display_str(run_date)

                if dt.is_holiday(run_date):
                    self.settings.save_task_execution_time(date_key, run_date)
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "It a is holiday."
                    self.output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                if not dt.is_data_refreshed(run_date, end_date):
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "Data is not refreshed yet."
                    self.output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                try:
                    execute_method(run_date, end_date_provided)

                except Exception as e:
                    message = f"Exception - `{format(e)}`."
                    self.tp.log_error(message=message)
                    self.output.append(self.message_creator(run_date_str, message))
                    raise

                run_date = dt.get_future_date(run_date, hours=pause_hours)

            self.tp.log_completed("Task Completed.")
            return self.output

    def __execute_equity_eod(self, run_date, end_date_provided):
        date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
        run_date_str = dt.datetime_to_display_str(run_date)

        re = self.load_equity_eod_data(run_date)
        reca = self.load_equity_corporate_action(run_date)
        red = self.load_equity_derivative_eod_data(run_date)
        self.tp.log_message("Equities - Data pull completed.", "Equities")

        if isinstance(re, str):
            self.output.append(self.message_creator(run_date_str, re))
            return

        with transaction.atomic():
            e_stats = self.__save_record(re, EquityEndOfDay, "Equities")
            d_stats = self.__save_record(red, EquityDerivativeEndOfDay, "Derivatives")
            self.__update_company_action(reca)

            stats = self.message_creator(run_date_str, [e_stats, d_stats])
            self.output.append(stats)
            if not end_date_provided:
                self.settings.save_task_execution_time(date_key, run_date)

    def execute_equity_eod_data_task(self, run_date=None, end_date=None):
        date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
        pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS
        default_start_key = sk.DEFAULT_START_DATE_EQUITY_DATA_PULL
        return self.__execute_eod_data_task(
            run_date,
            end_date,
            date_key,
            pause_hour_key,
            default_start_key,
            self.__execute_equity_eod,
        )

    def __execute_index_eod(self, run_date, end_date_provided):
        date_key = sk.DATAPULL_INDICES_EOD_LAST_PULL_DATE
        run_date_str = dt.datetime_to_display_str(run_date)

        re = self.load_index_eod_data(run_date)
        red = self.load_index_derivative_eod_data(run_date)
        self.tp.log_message("Indices - Data pull completed.", "Indices")

        if isinstance(re, str):
            self.output.append(self.message_creator(run_date_str, re))
            return

        with transaction.atomic():
            e_stats = self.__save_record(re, IndexEndOfDay, "Index")
            d_stats = self.__save_record(red, IndexDerivativeEndOfDay, "Derivatives")

            stats = self.message_creator(run_date_str, [e_stats, d_stats])
            self.output.append(stats)
            if not end_date_provided:
                self.settings.save_task_execution_time(date_key, run_date)

    def execute_index_eod_data_task(self, run_date=None, end_date=None):
        date_key = sk.DATAPULL_INDICES_EOD_LAST_PULL_DATE
        pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS
        default_start_key = sk.DEFAULT_START_DATE_INDEX_DATA_PULL
        return self.__execute_eod_data_task(
            run_date,
            end_date,
            date_key,
            pause_hour_key,
            default_start_key,
            self.__execute_index_eod,
        )

    def __execute_participant_eod(self, run_date, end_date_provided):
        date_key = sk.DATAPULL_PARTICIPANT_EOD_LAST_PULL_DATE
        run_date_str = dt.datetime_to_display_str(run_date)

        pt = self.load_participant_eod_data(run_date)
        pts = self.load_participant_stats_eod_data(run_date)

        if isinstance(pt, str):
            self.output.append(self.message_creator(run_date_str, pt))
            return

        with transaction.atomic():
            e_stats = self.__save_record(pt, ParticipantActivity, "Participant")
            d_stats = self.__save_record(
                pts, ParticipantStatsActivity, "Participant Stats"
            )

            stats = self.message_creator(run_date_str, [e_stats, d_stats])
            self.output.append(stats)
            if not end_date_provided:
                self.settings.save_task_execution_time(date_key, run_date)

    def execute_participant_eod_data_task(self, run_date=None, end_date=None):
        date_key = sk.DATAPULL_PARTICIPANT_EOD_LAST_PULL_DATE
        pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS
        default_start_key = sk.DEFAULT_START_DATE_PARTICIPANT_DATA_PULL
        return self.__execute_eod_data_task(
            run_date,
            end_date,
            date_key,
            pause_hour_key,
            default_start_key,
            self.__execute_participant_eod,
        )
