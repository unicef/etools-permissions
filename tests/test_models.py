from django.db.utils import IntegrityError

from tests.base import BaseTestCase, SCHEMA_NAME
from tests.factories import GroupFactory, OrganizationFactory, PermissionFactory, RealmFactory, UserFactory

from etools_permissions.models import Group, Permission, Realm


class TestPermission(BaseTestCase):
    def test_str(self):
        permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="etools_permissions.permission.*"
        )
        self.assertEqual(
            str(permission),
            "Allow permission to view etools_permissions.permission.* at []"
        )

    def test_filter_by_targets_for_wildcards(self):
        permission = PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.*'
        )

        targets = [
            'etools_permissions.permission.permission',
            'etools_permissions.permission.permission_type',
            'etools_permissions.permission.target',
        ]
        permissions = Permission.objects.filter_by_targets(targets)
        self.assertSequenceEqual(permissions, [permission])

    def test_filter_by_targets_empty(self):
        PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.*'
        )

        targets = [
            'etools_permissions.group.*',
        ]
        permissions = Permission.objects.filter_by_targets(targets)
        self.assertSequenceEqual(permissions, [])

    def test_filter_by_targets(self):
        permission = PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.*'
        )

        targets = [
            'etools_permissions.permission.*',
            'etools_permissions.group.*'
        ]
        permissions = Permission.objects.filter_by_targets(targets)
        self.assertSequenceEqual(permissions, [permission])

    def test_filter_by_context(self):
        permission = PermissionFactory(
            permission=Permission.VIEW,
            target="etools_permissions.permission.*",
            condition=["basic"]
        )
        contexts = [
            "basic"
        ]
        permissions = Permission.objects.filter_by_context(contexts)
        self.assertSequenceEqual(permissions, [permission])

    def test_filter_by_context_empty(self):
        PermissionFactory(
            permission=Permission.VIEW,
            target="etools_permissions.permission.*",
            condition=["basic"]
        )
        contexts = [
            "wrong"
        ]
        permissions = Permission.objects.filter_by_context(contexts)
        self.assertSequenceEqual(permissions, [])

    def test_filter_by_context_list(self):
        permission = PermissionFactory(
            permission=Permission.VIEW,
            target="etools_permissions.permission.*",
            condition=["basic"]
        )
        contexts = [
            ["basic"]
        ]
        permissions = Permission.objects.filter_by_context(contexts)
        self.assertSequenceEqual(permissions, [permission])

    def test_get_target(self):
        PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target='etools_permissions.permission.*'
        )
        target = Permission.get_target(Permission, "permission")
        self.assertEqual(target, "etools_permissions.permission.permission")

    def test_apply_permissions_different_kinds(self):
        PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target='etools_permissions.permission.permission'
        )
        PermissionFactory(
            permission=Permission.EDIT,
            permission_type=Permission.TYPE_ALLOW,
            target='etools_permissions.permission.target'
        )

        targets = [
            'etools_permissions.permission.permission',
            'etools_permissions.permission.permission_type',
            'etools_permissions.permission.target',
        ]

        allowed_targets = Permission.apply_permissions(
            Permission.objects.all(),
            targets,
            Permission.VIEW
        )
        self.assertSequenceEqual(
            allowed_targets,
            [
                'etools_permissions.permission.permission',
                'etools_permissions.permission.target'
            ]
        )

        allowed_targets = Permission.apply_permissions(
            Permission.objects.all(),
            targets,
            Permission.EDIT,
        )
        self.assertSequenceEqual(
            allowed_targets,
            ['etools_permissions.permission.target']
        )

    def test_apply_permissions_order(self):
        PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target='etools_permissions.permission.*'
        )
        PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.target',
            permission_type=Permission.TYPE_DISALLOW,
        )
        PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.permission_type',
            permission_type=Permission.TYPE_DISALLOW,
            condition=['condition1']
        )

        targets = [
            'etools_permissions.permission.permission',
            'etools_permissions.permission.permission_type',
            'etools_permissions.permission.target',
        ]

        allowed_targets = Permission.apply_permissions(
            Permission.objects.all(),
            targets,
            Permission.VIEW,
        )
        self.assertSequenceEqual(
            allowed_targets,
            ['etools_permissions.permission.permission']
        )

        PermissionFactory(
            permission=Permission.VIEW,
            target='etools_permissions.permission.target',
            permission_type=Permission.TYPE_ALLOW,
            condition=['condition1', 'condition2']
        )

        allowed_targets = Permission.apply_permissions(
            Permission.objects.all(),
            targets,
            Permission.VIEW,
        )
        self.assertSequenceEqual(
            allowed_targets,
            [
                'etools_permissions.permission.target',
                'etools_permissions.permission.permission'
            ]
        )


class TestGroup(BaseTestCase):
    def test_str(self):
        group = GroupFactory(name="Group")
        self.assertEqual(str(group), "Group")

    def test_natural_key(self):
        group = GroupFactory(name="Group")
        self.assertEqual(group.natural_key(), ("Group",))

    def test_get_by_natural_key(self):
        group = GroupFactory(name="Group")
        self.assertEqual(Group.objects.get_by_natural_key("Group"), group)


class TestRealm(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.permission = PermissionFactory(
            permission_type=Permission.TYPE_ALLOW,
            permission=Permission.EDIT,
        )
        self.permission_label = "{}.{}.{}".format(
            self.permission.permission_type,
            self.permission.permission,
            self.permission.target,
        )

    def test_str_user(self):
        r = Realm(user=self.user)
        self.assertEqual(str(r), self.user.username)

    def test_str_user_workspace(self):
        r = Realm(user=self.user, workspace=self.tenant)
        self.assertEqual(str(r), "{} {}".format(
            self.user.username,
            SCHEMA_NAME
        ))

    def test_str_user_workspace_organization(self):
        org = OrganizationFactory(name="Org")
        r = Realm(user=self.user, workspace=self.tenant, organization=org)
        self.assertEqual(str(r), "{} {} Org".format(
            self.user.username,
            SCHEMA_NAME
        ))

    def test_str_user_organization(self):
        org = OrganizationFactory(name="Org")
        r = Realm(user=self.user, organization=org)
        self.assertEqual(str(r), "{} Org".format(self.user.username))

    def test_save_no_workspace(self):
        org = OrganizationFactory(name="Org")
        with self.settings(AUTH_REQUIRES_WORKSPACE=False):
            r = Realm(user=self.user, organization=org)
            r.save()
        self.assertIsNone(r.workspace)

    def test_save_no_workspace_exception(self):
        org = OrganizationFactory(name="Org")
        with self.settings(AUTH_REQUIRES_WORKSPACE=True):
            with self.assertRaisesRegexp(IntegrityError, "Workspace value"):
                r = Realm(user=self.user, organization=org)
                r.save()
        self.assertIsNone(r.workspace)

    def test_save_no_organization(self):
        with self.settings(AUTH_REQUIRES_ORGANIZATION=False):
            r = Realm(user=self.user, workspace=self.tenant)
            r.save()

    def test_save_no_organization_exception(self):
        with self.settings(AUTH_REQUIRES_ORGANIZATION=True):
            with self.assertRaisesRegexp(IntegrityError, "Organization value"):
                r = Realm(user=self.user, workspace=self.tenant)
                r.save()

    def test_get_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = realm.get_group_permissions()
        self.assertEqual(len(perms), 0)

    def test_get_permissions(self):
        group = GroupFactory()
        group.permissions.add(self.permission)
        realm = RealmFactory(workspace=self.tenant)
        realm.groups.add(group)
        perms = realm.get_group_permissions()
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_get_all_permissions(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.permissions.add(self.permission)
        perms = realm.get_all_permissions()
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_has_perm_superuser(self):
        user = UserFactory(is_superuser=True)
        realm = RealmFactory(user=user, workspace=self.tenant)
        self.assertTrue(realm.has_perm(self.permission.target))

    def test_has_perm_false(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertFalse(realm.has_perm(self.permission.target))

    def test_has_perm(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.permissions.add(self.permission)
        self.assertTrue(realm.has_perm(self.permission.target))

    def test_has_perms_false(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertFalse(realm.has_perms([self.permission.target]))

    def test_has_perms(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.permissions.add(self.permission)
        self.assertTrue(realm.has_perms([self.permission.target]))
