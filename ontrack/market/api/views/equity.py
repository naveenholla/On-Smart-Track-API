from rest_framework import generics

from ontrack.market.api.serializers import lookup
from ontrack.market.models.lookup import Equity
from ontrack.utils.base.mixins import StaffEditorPermissionMixin


class EquityListCreateAPIView(StaffEditorPermissionMixin, generics.ListCreateAPIView):
    serializer_class = lookup.EquityListCreateSerializer

    filterset_fields = ["symbol", "exchange"]
    search_fields = (
        "^symbol",
        "name",
    )
    ordering_fields = ("id",)

    def get_queryset(self):
        queryset = Equity.backend.select_related("exchange")
        symbol = self.request.query_params.get("symbol")
        if symbol is not None:
            queryset = queryset.filter(symbol__iexact=symbol)
        return queryset


class EquityDetailAPIView(StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Equity.backend.all()
    serializer_class = lookup.EquityDetailsSerializer
    lookup_field = "slug__iexact"
