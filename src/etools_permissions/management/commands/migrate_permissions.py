from collections import defaultdict

from django.core.management import BaseCommand
from django.contrib.auth.models import (
    Group as GroupDjango,
    Permission as PermissionDjango
)

from etools_permissions.models import Group, Permission


def get_permission(codename):
    edit_prefix_list = ["add_", "change_", "delete_"]
    permission = Permission.VIEW
    for edit_prefix in edit_prefix_list:
        if codename.startswith(edit_prefix):
            permission = Permission.EDIT
    return permission


def get_permission_group_map():
    permission_map = defaultdict(list)
    for group in GroupDjango.objects.all():
        for perm in group.permissions.all():
            permission_map[perm.pk].append(group.name)
    return permission_map


def migrate_permissions():
    """Migrate all django permissions to etools permissions

    For each permisssion convert `add`/`change`/`delete` to `edit`,
    rest are considered `view`

    Set relation to relevant group.
    """
    permission_map = get_permission_group_map()
    for perm_django in PermissionDjango.objects.all():
        app_label = perm_django.content_type.app_label
        model_name = perm_django.content_type.model
        permission = get_permission(perm_django.codename)
        target = "{app_label}.{model_name}.*".format(
            app_label=app_label,
            model_name=model_name,
        )
        perm, _ = Permission.objects.get_or_create(
            permission=permission,
            permission_type=Permission.TYPE_ALLOW,
            target=target,
            condition=[],
        )
        for group_name in permission_map[perm_django.pk]:
            group = Group.objects.get(name=group_name)
            group.permissions.add(perm)


def migrate_groups():
    """Migrate all groups from django groups to etools permission groups"""
    for group_django in GroupDjango.objects.all():
        Group.objects.get_or_create(name=group_django.name)


class Command(BaseCommand):
    help = 'Migrate from permissions2 to etools_permissions'

    def handle(self, *args, **options):
        migrate_groups()
        migrate_permissions()
