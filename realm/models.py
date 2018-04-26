from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group, Permission#, AbstractUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _


# class User(AbstractUser):
#     # All methods to get permissions for a user needs to go through
#     # the Realm class, so we clear the permission methods for the User
#     get_group_permissions = None
#     get_all_permissions = None
#     has_perm = None
#     has_perms = None
#     has_module_perms = None


class Realm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    workspace = models.ForeignKey(settings.WORKSPACE_MODEL, null=True)
    organization = models.ForeignKey(settings.ORGANIZATION_MODEL, null=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this realm belongs to. A realm will get all '
            'permissions granted to each of their groups.'
        ),
        related_name="realm_set",
        related_query_name="realm",
    )
    realm_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('realm permissions'),
        blank=True,
        help_text=_('Specific permissions for this realm.'),
        related_name="realm_set",
        related_query_name="realm",
    )

    def __str__(self):
        return " ".join([
            str(x) for x in [self.user, self.workspace, self.organization]
            if x is not None
        ])

    def save(self, *args, **kwargs):
        if settings.AUTH_REQUIRES_WORKSPACE and not self.workspace:
            raise IntegrityError(_('Workspace value is required'))
        if settings.AUTH_REQUIRES_ORGANIZATION and not self.organization:
            raise IntegrityError(_('Organization value is required'))
        return super(Realm, self).save(*args, **kwargs)

    def get_group_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        groups. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self, obj))
        return permissions

    def has_perm(self, perm, obj=None):
        """
        Return True if the realm has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a realm that has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.user.is_active and self.user.is_superuser:
            return True

        # Otherwise we need to check the backends.
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_perm'):
                continue
            try:
                if backend.has_perm(self, perm, obj):
                    return True
            # A backend can raise `PermissionDenied` to short-circuit
            # permission checking.
            except PermissionDenied:
                return False
        return False

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the realm has each of the specified permissions. If
        object is passed, check if the realm has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use simlar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.user.is_active and self.user.is_superuser:
            return True

        for backend in auth.get_backends():
            if not hasattr(backend, 'has_module_perms'):
                continue
            try:
                if backend.has_module_perms(self, app_label):
                    return True
            # A backend can raise `PermissionDenied` to short-circuit
            # permission checking.
            except PermissionDenied:
                return False
        return False
