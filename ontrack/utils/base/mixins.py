from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions

from .permissions import IsStaffEditorPermission


class SuperAdminPermissionMixin:
    permission_classes = [permissions.IsAdminUser]


class StaffEditorPermissionMixin(LoginRequiredMixin):
    permission_classes = [permissions.IsAdminUser, IsStaffEditorPermission]
