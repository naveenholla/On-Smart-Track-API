# from django.db import transaction
# from django.db.models import Avg
# from ontrack.utils.datetime import DateTimeHelper
# from ontrack.utils.numbers import NumberHelper


# class EquityDataPullLogic:

#     @transaction.atomic
#     def save_equity_eod_data(self, data, equities, date):
#         records_to_create = []
#         records_to_update = []
#         for _, record in data.iterrows():
#             equity = equities.unique_search(record).first()

#             if equity is None:
#                 self.logger.log_warning(
#                     f"Can't find equity with name [symbol='{record['symbol']}',date='{record['date']}']."
#                 )
#                 equity = Equity(name=record["symbol"], symbol=record["symbol"])
#                 equity.save()

#             record["date"] = DateTimeHelper.str_to_datetime(record["date"], "%d-%b-%Y")
#             records_for_average = EquityEndOfDay.backend.get_records_after_date(
#                 query=record
#             )
#             average_values = records_for_average.aggregate(
#                 average_quantity_per_trade=Avg("quantity_per_trade"),
#                 average_volumn=Avg("traded_quantity"),
#                 average_delivery_percentage=Avg("delivery_quantity"),
#                 average_open_interest=Avg("open_interest"),
#             )
#             d = EquityEndOfDay(
#                 equity=equity,
#                 prev_close=NumberHelper.str_to_float(record["prev_close"]),
#                 open_price=NumberHelper.str_to_float(record["open_price"]),
#                 high_price=NumberHelper.str_to_float(record["high_price"]),
#                 low_price=NumberHelper.str_to_float(record["low_price"]),
#                 last_price=NumberHelper.str_to_float(record["last_price"]),
#                 close_price=NumberHelper.str_to_float(record["close_price"]),
#                 avg_price=NumberHelper.str_to_float(record["avg_price"]),
#                 traded_quantity=NumberHelper.str_to_float(record["traded_quantity"]),
#                 turn_overs_in_lacs=NumberHelper.str_to_float(
#                     record["turn_overs_in_lacs"]
#                 ),
#                 number_of_trades=NumberHelper.str_to_float(record["number_of_trades"]),
#                 delivery_quantity=NumberHelper.str_to_float(
#                     record["delivery_quantity"]
#                 ),
#                 delivery_percentage=NumberHelper.str_to_float(
#                     record["delivery_percentage"]
#                 ),
#                 date=record["date"],
#                 updated_at=DateTimeHelper.current_date_time(),
#                 created_at=DateTimeHelper.current_date_time(),
#             )

#             d.point_changed = d.close_price - d.prev_close
#             d.percentage_changed = d.point_changed / d.last_price * 100
#             d.quantity_per_trade = d.traded_quantity / d.number_of_trades

#             d.open_interest = 0
#             d.promotor_holding_percentage = 0

#             d.average_quantity_per_trade = average_values["average_quantity_per_trade"]
#             d.average_volumn = average_values["average_volumn"]
#             d.average_delivery_percentage = average_values[
#                 "average_delivery_percentage"
#             ]
#             d.average_open_interest = average_values["average_open_interest"]

#             records_to_create.append(d)

#         EquityEndOfDay.backend.bulk_create_or_update(
#             records_to_create,
#             records_to_update,
#             [
#                 "equity",
#                 "prev_close",
#                 "open_price",
#                 "high_price",
#                 "low_price",
#                 "last_price",
#                 "close_price",
#                 "avg_price",
#                 "traded_quantity",
#                 "turn_overs_in_lacs",
#                 "number_of_trades",
#                 "delivery_quantity",
#                 "delivery_percentage",
#                 "date",
#                 "updated_at",
#             ],
#         )

#         self.save_pull_equity_eod_data_task_time(date)
#         return f"{len(records_to_create)} records created, {len(records_to_update)} records updated."
