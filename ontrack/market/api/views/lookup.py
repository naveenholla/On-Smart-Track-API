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


class ExchangeListCreateAPIView(StaffEditorPermissionMixin, generics.ListCreateAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeListCreateSerializer


class ExchangeDetailAPIView(StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Exchange.backend.all()
    serializer_class = lookup.ExchangeDetailsSerializer


class EndOfDayTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        task_name = request.data.get("task_name")
        obj = InitializeData(exchange)
        result = obj.execute_equity_lookup_data_task()
        return Response(
            data={"result": result, "exchange": exchange, "task_name": task_name}
        )
