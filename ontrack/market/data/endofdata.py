from ontrack.market.data.common import CommonData
from ontrack.market.data.equity import PullEquityData
from ontrack.market.data.index import PullIndexData
from ontrack.market.data.participant import PullParticipantData
from ontrack.market.models.equity import EquityDerivativeEndOfDay, EquityEndOfDay
from ontrack.market.models.index import IndexDerivativeEndOfDay, IndexEndOfDay
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)
from ontrack.utils.logger import ApplicationLogger


class EndOfDayData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonData()
        self.exchange_symbol = exchange_symbol

    def load_equity_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()
        equity_eod_qs = EquityEndOfDay.backend.all()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol, exchange_qs, equity_qs, equity_eod_qs
        )

        result = pull_equity_obj.pull_parse_eod_data(date)
        if save_data:
            self.commonobj.create_or_update(result, EquityEndOfDay)

        return result

    def load_equity_derivative_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()
        equity_eod_qs = EquityEndOfDay.backend.all()
        equity_derivative_eod_qs = EquityDerivativeEndOfDay.backend.all()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
            equity_eod_qs,
            equity_derivative_eod_qs,
        )

        result = pull_equity_obj.pull_parse_derivative_eod_data(date)
        if save_data:
            self.commonobj.create_or_update(result, EquityDerivativeEndOfDay)

        return result

    def load_index_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        index_qs = Index.backend.all()
        index_eod_qs = IndexEndOfDay.backend.all()

        pull_index_obj = PullIndexData(
            self.exchange_symbol, exchange_qs, index_qs, index_eod_qs
        )

        result = pull_index_obj.pull_parse_eod_data(date)
        if save_data:
            self.commonobj.create_or_update(result, IndexEndOfDay)

        return result

    def load_index_derivative_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        index_qs = Index.backend.all()
        index_eod_qs = IndexEndOfDay.backend.all()
        index_derivative_eod_qs = IndexDerivativeEndOfDay.backend.all()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
            index_eod_qs,
            index_derivative_eod_qs,
        )

        result = pull_index_obj.pull_parse_derivative_eod_data(date)
        if save_data:
            self.commonobj.create_or_update(result, IndexDerivativeEndOfDay)

        return result

    def load_participant_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        participant_qs = ParticipantActivity.backend.all()

        pull_particpant_obj = PullParticipantData(
            self.exchange_symbol,
            exchange_qs,
            participant_qs,
        )

        result = pull_particpant_obj.pull_parse_eod_data(date)
        if save_data:
            self.commonobj.create_or_update(result, ParticipantActivity)

        return result

    def load_participant_stats_eod_data(self, date, save_data=True):
        exchange_qs = Exchange.backend.all()
        participant_qs = ParticipantActivity.backend.all()
        participant_stats_qs = ParticipantStatsActivity.backend.all()

        pull_particpant_obj = PullParticipantData(
            self.exchange_symbol,
            exchange_qs,
            participant_qs,
            participant_stats_qs,
        )

        result = pull_particpant_obj.pull_parse_eod_stats(date)
        if save_data:
            self.commonobj.create_or_update(result, ParticipantStatsActivity)

        return result

    def load_eod_data(self, date):
        self.load_equity_eod_data(date)
        self.load_index_eod_data(date)

        self.load_equity_derivative_eod_data(date)
        self.load_index_derivative_eod_data(date)

        self.load_participant_eod_data(date)
