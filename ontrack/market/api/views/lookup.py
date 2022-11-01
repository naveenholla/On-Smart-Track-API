from rest_framework.decorators import api_view
from rest_framework.response import Response

from ontrack.market.api.serializers.lookup import ExchangeSerializer
from ontrack.market.models.lookup import Exchange


@api_view(["GET"])
def api_home(request, *args, **kwargs):
    instance = Exchange.backend.unique_search("nse").first()
    data = {}
    if instance:
        data = ExchangeSerializer(instance).data

    return Response(data)
