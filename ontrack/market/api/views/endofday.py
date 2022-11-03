from rest_framework.response import Response
from rest_framework.views import APIView

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.utils.base.mixins import SuperAdminPermissionMixin
from ontrack.utils.datetime import DateTimeHelper as dt


class EquityEndOfDayDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        obj = EndOfDayData(exchange)
        result = obj.execute_equity_eod_data_task()
        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "exchange": exchange,
                "result": result,
            }
        )
