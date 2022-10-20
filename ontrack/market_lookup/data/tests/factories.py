from factory.django import DjangoModelFactory

from ontrack.market_lookup.models.lookup import Equity, Exchange


class ExchangeFactory(DjangoModelFactory):

    name = "NSE"
    symbol = "nse"
    start_time = "09:15:00"
    end_time = "15:30:00"
    data_refresh_time = "20:00:00"
    time_zone = "Asia/Kolkata"

    class Meta:
        model = Exchange
        django_get_or_create = [
            "name",
            "symbol",
            "start_time",
            "end_time",
            "data_refresh_time",
            "time_zone",
        ]


class EquityFactory(DjangoModelFactory):

    name = "Reliance"
    symbol = "Reliance"
    chart_symbol = "Reliance"
    lot_size = 50
    strike_difference = 100
    is_active = True
    exchange = ExchangeFactory

    class Meta:
        model = Equity
        django_get_or_create = [
            "name",
            "symbol",
            "chart_symbol",
            "lot_size",
            "strike_difference",
            "is_active",
        ]
