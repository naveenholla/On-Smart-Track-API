from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ontrack.market.api.logic.lookup import InitializeData
from ontrack.market.api.serializers import lookup
from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.mixins import (
    StaffEditorPermissionMixin,
    SuperAdminPermissionMixin,
)
from ontrack.utils.datetime import DateTimeHelper as dt


class ExchangeListCreateAPIView(StaffEditorPermissionMixin, generics.ListCreateAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeListCreateSerializer


class ExchangeDetailAPIView(StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeDetailsSerializer


class InitialDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        obj = InitializeData("")
        result = obj.execute_initial_lookup_data_task()
        return Response(
            data={"datetime": dt.current_dt_display_str(), "result": result}
        )


class HolidaysLookupDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        obj = InitializeData(exchange)
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
        obj = InitializeData(exchange)
        result = obj.execute_market_lookup_data_task()
        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "exchange": exchange,
                "result": result,
            }
        )
