from django.db.utils import IntegrityError

from realm.models import Realm
from tests.base import SCHEMA_NAME, BaseTestCase
from tests.factories import (
    GroupFactory,
    OrganizationFactory,
    PermissionFactory,
    RealmFactory,
    UserFactory,
)


class TestRealm(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.permission = PermissionFactory()
        self.permission_app_label = self.permission.content_type.app_label
        self.permission_label = "{}.{}".format(
            self.permission_app_label,
            self.permission.codename
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
        with self.assertRaisesRegexp(IntegrityError, "Workspace value"):
            r = Realm(user=self.user, organization=org)
            r.save()
        self.assertIsNone(r.workspace)

    def test_save_no_organization(self):
        with self.settings(AUTH_REQUIRES_ORGANIZATION=False):
            r = Realm(user=self.user, workspace=self.tenant)
            r.save()

    def test_save_no_organization_exception(self):
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
        realm.realm_permissions.add(self.permission)
        perms = realm.get_all_permissions()
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_has_perm_superuser(self):
        user = UserFactory(is_superuser=True)
        realm = RealmFactory(user=user, workspace=self.tenant)
        self.assertTrue(realm.has_perm(self.permission_label))

    def test_has_perm_false(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertFalse(realm.has_perm(self.permission_label))

    def test_has_perm(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        self.assertTrue(realm.has_perm(self.permission_label))

    def test_has_perms_false(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertFalse(realm.has_perms([self.permission_label]))

    def test_has_perms(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        self.assertTrue(realm.has_perms([self.permission_label]))

    def test_has_module_perms_superuser(self):
        user = UserFactory(is_superuser=True)
        realm = RealmFactory(user=user, workspace=self.tenant)
        self.assertTrue(realm.has_module_perms(self.permission_app_label))

    def test_has_module_perms_false(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertFalse(realm.has_module_perms(self.permission_app_label))

    def test_has_module_perms(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        self.assertTrue(realm.has_module_perms(self.permission_app_label))
