from rest_framework import exceptions, serializers
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

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(
                    view.__class__.__name__
                )
            )
            return queryset
        return view.queryset

    def _permissions_by_queryset(self, method, view):
        """Get permissions based on the queryset used"""
        queryset = self._queryset(view)

        kwargs = {
            'app_label': queryset.model._meta.app_label,
            'model_name': queryset.model._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _permissions_by_serializer(self, method, serializer_cls):
        """Get permissions based on the serializer used

        Collect permissions targets based on serializer's model and
        field name from full serializers tree.
        """
        serializer = serializer_cls()
        targets = list()
        edit_type = ["PATCH", "POST", "PUT", "DELETE"]
        perm_type = Permission.EDIT if method in edit_type else Permission.VIEW

        # Breath-first search
        queue = [serializer.root]
        level = 3  # max depth
        while queue and level > 0:
            node = queue.pop(0)
            perm_type = Permission.VIEW if node.read_only else perm_type

            if isinstance(node, serializers.ListSerializer):
                queue.append(node.child)
                level -= 1
                continue

            node_fields = node.fields.values()

            for field in node_fields:
                targets.append("{}.{}".format(
                    perm_type,
                    Permission.get_target(node.Meta.model, field))
                )
                if isinstance(field, serializers.BaseSerializer):
                    queue.append(field)
                    level -= 1

        return targets

    def get_required_permissions(self, request, view):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        serializer_cls = view.get_serializer_class()
        if serializer_cls:
            return self._permissions_by_serializer(
                request.method,
                serializer_cls
            )
        return self._permissions_by_queryset(request.method, view)

    def has_permission(self, request, view):
        if getattr(view, '_ignore_permissions', False):
            return True

        if not request.user or not request.realm or (
                not request.user.is_authenticated and
                self.authenticated_users_only
        ):
            return False

        perms = self.get_required_permissions(request, view)
        return request.realm.has_perms(perms)
