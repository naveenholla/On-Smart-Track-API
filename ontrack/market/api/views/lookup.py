from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ontrack.lookup.tasks import (
    execute_initial_lookup_data_task as lookup_initial_data_task,
)
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.api.serializers import lookup
from ontrack.market.models.lookup import Exchange
from ontrack.market.tasks.lookup import (
    execute_initial_lookup_data_task as market_initial_data_task,
)
from ontrack.utils.base.mixins import SuperAdminPermissionMixin
from ontrack.utils.datetime import DateTimeHelper as dt


class ExchangeListCreateAPIView(SuperAdminPermissionMixin, generics.ListCreateAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeListCreateSerializer


class ExchangeDetailAPIView(SuperAdminPermissionMixin, generics.RetrieveAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeDetailsSerializer


class InitialDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        taskid = lookup_initial_data_task().delay()
        taskid2 = market_initial_data_task().delay()
        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "task_1": taskid,
                "task_2": taskid2,
            }
        )


class HolidaysLookupDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        obj = MarketLookupData(exchange)
        result = obj.execute_holidays_lookup_data_task()
        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "exchange": exchange,
                "result": result,
            }
        )


class MarketLookupDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        obj = MarketLookupData(exchange)
        result = obj.execute_market_lookup_data_task()
        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "exchange": exchange,
                "result": result,
            }
        )
