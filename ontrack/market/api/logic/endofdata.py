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
from ontrack.utils.base.manager import CommonLogic
from ontrack.utils.logger import ApplicationLogger


class EndOfDayData:
    def __init__(self, exchange_symbol: str):
        self.logger = ApplicationLogger()
        self.commonobj = CommonLogic()
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

    def load_equity_eod_data(self, date, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol, self.exchange_qs, self.equity_qs, self.equity_eod_qs
        )

        result = pull_equity_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.commonobj.create_or_update(result, EquityEndOfDay)

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
            records_stats = self.commonobj.create_or_update(
                result, EquityDerivativeEndOfDay
            )

        return result, records_stats

    def load_index_eod_data(self, date, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol, self.exchange_qs, self.index_qs, self.index_eod_qs
        )

        result = pull_index_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.commonobj.create_or_update(result, IndexEndOfDay)

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
            records_stats = self.commonobj.create_or_update(
                result, IndexDerivativeEndOfDay
            )

        return result, records_stats

    def load_participant_eod_data(self, date, save_data=True):
        pull_particpant_obj = PullParticipantData(
            self.exchange_symbol,
            self.exchange_qs,
            self.participant_qs,
        )

        result = pull_particpant_obj.pull_parse_eod_data(date)
        if save_data:
            records_stats = self.commonobj.create_or_update(result, ParticipantActivity)

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
            records_stats = self.commonobj.create_or_update(
                result, ParticipantStatsActivity
            )

        return result, records_stats

    def load_eod_data(self, date):
        self.load_equity_eod_data(date)
        self.load_index_eod_data(date)

        self.load_equity_derivative_eod_data(date)
        self.load_index_derivative_eod_data(date)

        self.load_participant_eod_data(date)
