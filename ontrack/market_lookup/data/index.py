from django.utils.text import slugify

from ontrack.market_lookup.queryset import ExchangeQuerySet, IndexQuerySet

from ...utils.logger import ApplicationLogger


class PullIndexData:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet = None,
        index_qs: IndexQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.index_qs = index_qs

    def parse_index_data(self, exchange_symbol: str, record: dict, market_cap_url: str):
        if self.exchange_qs is None:
            self.logger.log_warning("Exchange queyset is null.")
            return None

        exchange = self.exchange_qs.unique_search(exchange_symbol).first()
        if exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{exchange_symbol}' doesn't exists"
            )
            return None

        market_cap_records = self.pull_equity_marketlot_data(market_cap_url)

        symbol = record["symbol"]
        pk = None
        lot_size = record["lot_size"] if "lot_size" in record else 0
        existing_index = self.index_qs.unique_search(symbol).first()
        if existing_index is not None:
            pk = existing_index.id

        market_cap_record = [x for x in market_cap_records if x["symbol"] == symbol]
        if len(market_cap_record) > 0:
            lot_size = market_cap_record[0]["lot_size"]

        dict_record = {}
        dict_record["id"] = pk
        dict_record["exchange"] = {"symbol": exchange_symbol}
        dict_record["name"] = record["name"]
        dict_record["symbol"] = record["symbol"]
        dict_record["chart_symbol"] = (
            record["chart_symbol"] if "chart_symbol" in record else record["symbol"]
        )
        dict_record["lot_size"] = lot_size
        dict_record["ordinal"] = record["ordinal"]
        dict_record["slug"] = slugify(f"{exchange_symbol}_{record['symbol']}")
        dict_record["is_sectoral"] = record["is_sector"]
        dict_record["is_active"] = record["is_active"]
        dict_record["strike_difference"] = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        return dict_record
