from rest_framework.response import Response
from rest_framework.views import APIView

from ontrack.users.api.logic.accounts import AccountLogic


class DematAccountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # # exchange = request.query_params.get("exchange")
        # if not exchange:
        #     return Response(None)

        obj = AccountLogic(request.user)
        result = obj.get_all_demat_accounts()
        return Response(result)
