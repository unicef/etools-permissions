from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from realm.models import Permission, Realm


class RealmBackend(ModelBackend):
    def _get_realm(self, user):
        try:
            return Realm.objects.get(user=user)
        except Realm.DoesNotExist:
            raise PermissionDenied

    def _get_realm_permissions(self, realm_obj):
        return realm_obj.realm_permissions.all()

    def _get_group_permissions(self, realm_obj):
        realm_groups_field = Realm._meta.get_field('groups')
        realm_groups_query = 'group__{}'.format(
            realm_groups_field.related_query_name()
        )
        return Permission.objects.filter(**{realm_groups_query: realm_obj})

    def _get_permissions(self, realm_obj, obj, from_name):
        """
        Return the permissions of `realm_obj` from `from_name`. `from_name` can
        be either "group" or "realm" to return permissions from
        `_get_group_permissions` or `_get_realm_permissions` respectively.
        """
        if not realm_obj.user.is_active or realm_obj.user.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_{}_perm_cache'.format(from_name)
        if not hasattr(realm_obj, perm_cache_name):
            if realm_obj.user.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(
                    self,
                    '_get_{}_permissions'.format(from_name)
                )(realm_obj)
            perms = perms.values_list(
                'permission',
                'permission_type',
                'target',
            ).order_by()
            setattr(
                realm_obj,
                perm_cache_name,
                {"{}.{}".format(
                    perm,
                    target,
                ) for perm, perm_type, target in perms}
            )
        return getattr(realm_obj, perm_cache_name)

    def get_realm_permissions(self, realm_obj, obj=None):
        """
        Return a set of permission strings the realm `realm_obj` has from their
        `realm_permissions`.
        """
        return self._get_permissions(realm_obj, obj, 'realm')

    def get_group_permissions(self, realm_obj, obj=None):
        """
        Return a set of permission strings the realm `realm_obj` has from the
        groups they belong.
        """
        return self._get_permissions(realm_obj, obj, 'group')

    def get_all_permissions(self, realm_obj, obj=None):
        if not realm_obj.user.is_active or realm_obj.user.is_anonymous or obj is not None:
            return set()
        if not hasattr(realm_obj, '_perm_cache'):
            realm_obj._perm_cache = set()
            realm_obj._perm_cache.update(self.get_realm_permissions(realm_obj))
            realm_obj._perm_cache.update(self.get_group_permissions(realm_obj))
        return realm_obj._perm_cache

    def has_perm(self, user, perm, obj=None):
        if not user.is_active:
            return False
        return perm in self.get_all_permissions(self._get_realm(user), obj)

    def has_module_perms(self, realm_obj, app_label):
        """
        Return True if realm_obj has any permissions in the given app_label.
        """
        if not realm_obj.user.is_active:
            return False
        for perm in self.get_all_permissions(realm_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False
