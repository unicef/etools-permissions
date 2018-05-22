from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from etools_permissions.models import Permission, Realm


class RealmBackend(ModelBackend):
    def _get_realm(self, user):
        try:
            return Realm.objects.get(user=user)
        except Realm.DoesNotExist:
            raise PermissionDenied

    def _get_realm_permissions(self, realm):
        return realm.realm_permissions.all()

    def _get_group_permissions(self, realm):
        realm_groups_field = Realm._meta.get_field('groups')
        realm_groups_query = 'group__{}'.format(
            realm_groups_field.related_query_name()
        )
        return Permission.objects.filter(**{realm_groups_query: realm})

    def _get_permissions(self, realm, obj, from_name):
        """
        Return the permissions of `realm` from `from_name`. `from_name` can
        be either "group" or "realm" to return permissions from
        `_get_group_permissions` or `_get_realm_permissions` respectively.
        """
        if not realm.user.is_active or realm.user.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_{}_perm_cache'.format(from_name)
        if not hasattr(realm, perm_cache_name):
            if realm.user.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(
                    self,
                    '_get_{}_permissions'.format(from_name)
                )(realm)
            perms = perms.values_list(
                'permission',
                'permission_type',
                'target',
            ).order_by()
            setattr(
                realm,
                perm_cache_name,
                {"{}.{}.{}".format(
                    perm_type,
                    perm,
                    target,
                ) for perm, perm_type, target in perms}
            )
        return getattr(realm, perm_cache_name)

    def get_realm_permissions(self, realm, obj=None):
        """
        Return a set of permission strings the `realm` has from their
        `realm_permissions`.
        """
        return self._get_permissions(realm, obj, 'realm')

    def get_group_permissions(self, realm, obj=None):
        """
        Return a set of permission strings the `realm` has from the
        groups they belong.
        """
        return self._get_permissions(realm, obj, 'group')

    def get_all_permissions(self, realm, obj=None):
        if not realm.user.is_active or realm.user.is_anonymous:
            return set()
        if not hasattr(realm, '_perm_cache'):
            realm._perm_cache = set()
            realm._perm_cache.update(self.get_realm_permissions(realm, obj))
            realm._perm_cache.update(self.get_group_permissions(realm, obj))
        return realm._perm_cache

    def _parse_target(self, target):
        """Target may have preceding data"""
        perm, actual_target = target.split(".", 1)
        # If we have any packages named "edit" or "view"
        # this falls apart! Doh!
        if perm in [Permission.EDIT, Permission.VIEW]:
            return perm, actual_target
        else:
            return None, target

    def perm_valid(self, permissions, target):
        """Check if target matches any permissions user has"""
        target_perm, target = self._parse_target(target)

        for permission in permissions:
            perm_type, perm, perm_target = permission.split(".", 2)
            if perm_type == Permission.TYPE_DISALLOW:
                continue

            if target_perm == Permission.EDIT and perm_type == Permission.VIEW:
                continue

            if perm_target[-1] == '*':
                if target.startswith(perm_target[:-1]):
                    return True

        return False

    def has_perm(self, user, perm, obj=None):
        if not user.is_active:
            return False
        permissions = self.get_all_permissions(self._get_realm(user), obj)
        return self.perm_valid(permissions, perm)

    # def has_module_perms(self, realm_obj, app_label):
    #     """
    #     Return True if realm_obj has any permissions in the given app_label.
    #     """
    #     if not realm_obj.user.is_active:
    #         return False
    #     for perm in self.get_all_permissions(realm_obj):
    #         if perm[:perm.index('.')] == app_label:
    #             return True
    #     return False
