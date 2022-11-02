from rest_framework import permissions


class IsStaffEditorPermission(permissions.DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user.is_staff:
            return False
        return super().has_permission(request, view)


class IsOwnerOrReadOnlyPermission(permissions.DjangoModelPermissions):
    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj) -> bool:

        if request.method is permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
