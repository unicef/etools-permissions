from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from realm.models import Permission


class RealmPermission(BasePermission):
    """In case of nesting views we need to check access
    to child relation from parent instance.
    """
    perms_map = {
        'GET': ['{}.%(app_label)s.%(model_name)s.*'.format(Permission.VIEW)],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['{}.%(app_label)s.%(model_name)s.*'.format(Permission.EDIT)],
        'PUT': ['{}.%(app_label)s.%(model_name)s.*'.format(Permission.EDIT)],
        'PATCH': ['{}.%(app_label)s.%(model_name)s.*'.format(Permission.EDIT)],
        'DELETE': ['{}.%(app_label)s.%(model_name)s.*'.format(
            Permission.EDIT
        )],
    }

    def get_parent(self, view):
        parent_class = getattr(view, 'parent', None)
        if not parent_class:
            return

        return parent_class(
            request=view.request,
            kwargs=view.kwargs,
            lookup_url_kwarg=view.parent_lookup_kwarg
        )

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        if getattr(view, '_ignore_permissions', False):
            return True

        if not request.user or not request.realm or (
                not request.user.is_authenticated and
                self.authenticated_users_only
        ):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        return request.realm.has_perms(perms)
