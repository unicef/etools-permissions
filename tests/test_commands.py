from django.contrib.auth.models import (
    Group as DjangoGroup,
    Permission as DjangoPermission,
)
from django.core.management import call_command

from etools_permissions.models import Group, Permission
from tests.base import BaseTestCase


class TestMigratePermissions(BaseTestCase):
    def test_command(self):
        django_group_qs = DjangoGroup.objects
        self.assertFalse(django_group_qs.count())
        group_qs = Group.objects
        self.assertFalse(group_qs.count())
        perm_qs = Permission.objects
        self.assertFalse(perm_qs.count())

        call_command("migrate_permissions")
        self.assertTrue(perm_qs.count() > 1)
        self.assertFalse(group_qs.count())

    def test_command_group(self):
        django_group_qs = DjangoGroup.objects
        perm = DjangoPermission.objects.first()
        group = DjangoGroup.objects.create(
            name="Test Group",
        )
        group.permissions.add(perm)
        self.assertEqual(django_group_qs.count(), 1)
        group_qs = Group.objects
        self.assertFalse(group_qs.count())
        perm_qs = Permission.objects
        self.assertFalse(perm_qs.count())

        call_command("migrate_permissions")
        self.assertTrue(perm_qs.count() > 1)
        self.assertEqual(group_qs.count(), 1)
        new_group = Group.objects.first()
        self.assertEqual(new_group.name, "Test Group")
        self.assertEqual(new_group.permissions.count(), 1)
