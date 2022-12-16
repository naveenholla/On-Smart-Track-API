from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from rest_framework.renderers import TemplateHTMLRenderer

from ontrack.users.models.lookup import DematAccount

User = get_user_model()


class DematAccountListView(LoginRequiredMixin, ListView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "users/accounts/demataccount.html"
    model = DematAccount


demat_account_list_view = DematAccountListView.as_view()
