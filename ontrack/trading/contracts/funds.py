class Funds:
    def __init__(self):
        self.available_cash = 0
        self.available_margin = 0
        self.used_margin = 0
        self.opening_balance = 0
        self.pay_in = 0
        self.pay_out = 0
        self.span_margin = 0
        self.delivery_margin = 0
        self.exposure = 0
        self.option_premium = 0
        self.collateral_liquid = 0
        self.collateral_equity = 0
        self.turnover = 0
        self.holding_sales = 0
        self.m2m_unrealised = 0
        self.m2m_realised = 0
        self.debits = 0

    def __str__(self):
        return (
            f"available_cash={self.available_cash}, "
            f"available_margin={self.available_margin}, "
            f"used_margin={self.used_margin}, "
            f"opening_balance={self.opening_balance}, "
            f"pay_in={self.pay_in}, "
            f"pay_out={self.pay_out}, "
            f"span_margin={self.span_margin}, "
            f"delivery_margin={self.delivery_margin}, "
            f"exposure={self.exposure}, "
            f"option_premium={self.option_premium}, "
            f"collateral_liquid={self.collateral_liquid}, "
            f"collateral_equity={self.collateral_equity}, "
            f"turnover={self.turnover}, "
        )
