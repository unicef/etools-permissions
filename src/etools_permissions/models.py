from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_backends
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _

from etools_permissions.conditions import BaseCondition
from etools_permissions.utils import collect_child_models, collect_parent_models


class PermissionQuerySet(models.QuerySet):
    def filter_by_context(self, context):
        context = list(context)
        i = 0
        while i < len(context):
            if isinstance(context[i], BaseCondition):
                context[i] = context[i].to_internal_value()

            if isinstance(context[i], (list, tuple)):
                context.extend(context[i])
                context.pop(i)
            else:
                i += 1

        return self.filter(condition__contained_by=context)

    def filter_by_targets(self, targets):
        targets = list(targets)

        i = 0
        parent_map = dict()
        while i < len(targets):
            target = targets[i]

            model, field_name = Permission.parse_target(target)
            if model in parent_map:
                parents = parent_map[model]
            else:
                parents = collect_parent_models(model, levels=1)
                parent_map[model] = parents

            targets.extend([Permission.get_target(parent, field_name) for parent in parents])

            i += 1

        wildcards = list(set([t.rsplit('.', 1)[0] + '.*' for t in targets]))
        targets = targets + wildcards

        return self.filter(target__in=targets)


class Permission(models.Model):
    """Model describes field-level permissions.

    Provide different set of readable/writable fields in dependency
    from current context.

    User roles and target state are defined in conditions, so we don't
    need to strongly determine user role.
    Then can be combined to grant more privileges for user in special cases.
    """

    VIEW = "view"
    EDIT = "edit"
    ACTION = "action"
    PERMISSION_CHOICES = (
        (VIEW, _('View')),
        (EDIT, _('Edit')),
        (ACTION, _('Action')),
    )

    TYPE_ALLOW = "allow"
    TYPE_DISALLOW = "disallow"
    TYPE_CHOICES = (
        (TYPE_ALLOW, _('Allow')),
        (TYPE_DISALLOW, _('Disallow')),
    )

    permission = models.CharField(
        max_length=10,
        verbose_name=_('permission'),
        choices=PERMISSION_CHOICES,
    )
    permission_type = models.CharField(
        max_length=10,
        verbose_name=_('permission type'),
        choices=TYPE_CHOICES,
        default=TYPE_ALLOW,
    )
    target = models.CharField(
        max_length=100,
        verbose_name=_('target'),
    )
    condition = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_('condition'),
        default=[],
        blank=True,
    )

    objects = PermissionQuerySet.as_manager()

    def __str__(self):
        return '{} permission to {} {} at {}'.format(
            self.permission_type.title(),
            self.permission,
            self.target,
            self.condition,
        )

    @staticmethod
    def get_target(model, field):
        if hasattr(field, 'name'):
            field = field.name
        elif hasattr(field, 'field_name'):
            field = field.field_name

        return '.'.join([model._meta.app_label, model._meta.model_name, field])

    @staticmethod
    def parse_target(target):
        app_label, model_name, field = target.split('.')
        model = apps.get_model(app_label, model_name)
        return model, field

    @classmethod
    def apply_permissions(cls, permissions, targets, kind):
        """apply permissions to targets"""
        permissions = list(permissions)

        i = 0
        children_map = dict()
        while i < len(permissions):
            perm = permissions[i]

            model, field_name = Permission.parse_target(perm.target)
            if model in children_map:
                children = children_map[model]
            else:
                children = collect_child_models(model, levels=1)
                children_map[model] = children

            # apply permissions to childs, in case of inheritance
            imaginary_permissions = [
                Permission(
                    permission=perm.permission,
                    permission_type=perm.permission_type,
                    condition=perm.condition,
                    target=Permission.get_target(child, field_name)
                )
                for child in children
            ]

            # permissions can be defined both for children and parent,
            # so we need to priority children permissions from automatically
            # generated parent-based permissions.
            perm.image_level = getattr(perm, 'image_level', 0)
            for imaginary_perm in imaginary_permissions:
                imaginary_perm.image_level = perm.image_level + 1

            permissions.extend(imaginary_permissions)

            i += 1

        # order permissions in dependency from their level
        # and complexity of condition
        permissions.sort(
            key=lambda perm: (
                perm.image_level, -len(perm.condition), '*' in perm.target
            )
        )

        allowed_targets = []
        targets = set(targets)
        for perm in permissions:
            if kind == cls.VIEW and perm.permission_type == cls.TYPE_ALLOW:
                # If you can edit field you can view it too.
                if perm.permission not in [cls.VIEW, cls.EDIT]:
                    continue
            elif perm.permission != kind:
                continue

            if perm.target[-1] == '*':
                affected_targets = set(
                    [t for t in targets if t.startswith(perm.target[:-1])]
                )
            else:
                affected_targets = {perm.target}

            if not affected_targets:
                continue

            if perm.permission_type == cls.TYPE_ALLOW and affected_targets & targets:
                allowed_targets.extend(affected_targets)

            targets -= affected_targets

        return allowed_targets


class GroupManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Group(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


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
        for backend in get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        permissions = set()
        for backend in get_backends():
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
        for backend in get_backends():
            if not hasattr(backend, 'has_perm'):
                continue
            try:
                if backend.has_perm(self.user, perm, obj):
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

    # def has_module_perms(self, app_label):
    #     """
    #     Return True if the user has any permissions in the given app label.
    #     Use simlar logic as has_perm(), above.
    #     """
    #     # Active superusers have all permissions.
    #     if self.user.is_active and self.user.is_superuser:
    #         return True

    #     for backend in get_backends():
    #         if not hasattr(backend, 'has_module_perms'):
    #             continue
    #         try:
    #             if backend.has_module_perms(self, app_label):
    #                 return True
    #         # A backend can raise `PermissionDenied` to short-circuit
    #         # permission checking.
    #         except PermissionDenied:
    #             return False
    #     return False
