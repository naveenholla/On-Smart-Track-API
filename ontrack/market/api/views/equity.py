from rest_framework import generics

from ontrack.market.api.serializers import lookup
from ontrack.market.models.lookup import Equity
from ontrack.utils.base.mixins import StaffEditorPermissionMixin


class EquityListCreateAPIView(StaffEditorPermissionMixin, generics.ListCreateAPIView):
    queryset = Equity.backend.all()
    serializer_class = lookup.EquityListCreateSerializer

    filterset_fields = ["symbol", "exchange"]
    search_fields = (
        "^symbol",
        "name",
    )
    ordering_fields = ("id",)

    def get_queryset(self):
        queryset = Equity.backend.all()
        symbol = self.request.query_params.get("symbol")
        if symbol is not None:
            queryset = queryset.filter(symbol__iexact=symbol)

        # queryset.annotate(
        #     _average_traded_quantity=Subquery(EquityEndOfDay.backend.filter(entity=OuterRef('pk')).order_by('-date').values('pk')[:1])
        # )

        # queryset = queryset.annotate(_delivery_quantity=Avg('eod_data__delivery_quantity'))
        return queryset


class EquityDetailAPIView(StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Equity.backend.all()
    serializer_class = lookup.EquityDetailsSerializer
    lookup_field = "slug__iexact"

    # def get_queryset(self):
    #     slug = self.kwargs.get("slug__iexact")
    #     queryset = Equity.backend.filter(slug__iexact=slug)
    #     queryset.annotate(
    #         _lastest_eod_data_id=Subquery(
    #             EquityEndOfDay.backend.filter(entity=OuterRef("pk"))
    #             .order_by("-date")
    #             .values("pk")[:1]
    #         )
    #     )
    #     return queryset
