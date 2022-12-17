from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from ontrack.users.api.views.accounts import DematAccountAPIView


class DematAccountListView(LoginRequiredMixin, TemplateView):
    template_name = "users/accounts/demataccount.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view = DematAccountAPIView.as_view()
        response = view(request=self.request)
        data = response.data
        context["accounts"] = data
        return context


demat_account_list_view = DematAccountListView.as_view()


@login_required
@require_http_methods(["POST"])
def demat_login_view(request, id):
    view = DematAccountAPIView.as_view()
    response = view(request=request)
    data = response.data
    context = {}
    context["accounts"] = data

    return render(request, "users/accounts/partials/demat-list.html", context=context)
