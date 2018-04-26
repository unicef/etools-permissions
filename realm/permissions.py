from django.http import Http404
from rest_framework.permissions import (
    DjangoModelPermissions,
    DjangoObjectPermissions,
    SAFE_METHODS,
)


class RealmModelPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or not request.realm or (
                not request.user.is_authenticated and
                self.authenticated_users_only
        ):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return request.realm.has_perms(perms)


class RealmObjectPermissions(DjangoObjectPermissions):
    def has_object_permission(self, request, view, obj):
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        realm = request.realm

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not realm.has_perms(perms, obj):
            # If the realm does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not realm.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False

        return True
