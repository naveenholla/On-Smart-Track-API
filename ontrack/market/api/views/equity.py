from rest_framework import generics

from ontrack.market.api.serializers import lookup
from ontrack.market.models.lookup import Equity
from ontrack.utils.base.mixins import StaffEditorPermissionMixin


class EquityListCreateAPIView(StaffEditorPermissionMixin, generics.ListCreateAPIView):
    queryset = Equity.backend.all()
    serializer_class = lookup.EquityListCreateSerializer


class EquityDetailAPIView(StaffEditorPermissionMixin, generics.RetrieveAPIView):
    queryset = Equity.backend.all()
    serializer_class = lookup.EquityListCreateSerializer
    lookup_field = "slug__iexact"
