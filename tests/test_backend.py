from django.core.exceptions import PermissionDenied

from realm.backends import RealmBackend
from realm.models import Permission
from tests.base import BaseTestCase
from tests.factories import (
    GroupFactory,
    PermissionFactory,
    RealmFactory,
    UserFactory,
)


class TestRealmBackend(BaseTestCase):
    def setUp(self):
        self.permission = PermissionFactory(
            permission_type=Permission.TYPE_ALLOW,
            permission=Permission.EDIT,
        )
        self.permission_label = "{}.{}.{}".format(
            self.permission.permission_type,
            self.permission.permission,
            self.permission.target,
        )
        self.backend = RealmBackend()

    def test_get_realm_exception(self):
        with self.assertRaises(PermissionDenied):
            self.backend._get_realm(None)

    def test_get_realm(self):
        user = UserFactory()
        realm = RealmFactory(user=user, workspace=self.tenant)
        self.assertEqual(self.backend._get_realm(user), realm)

    def test_internal_get_realm_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertEqual(len(self.backend._get_realm_permissions(realm)), 0)

    def test_internal_get_realm_permissions(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        perms = self.backend._get_realm_permissions(realm)
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission, perms)

    def test_internal_get_group_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        self.assertEqual(len(self.backend._get_group_permissions(realm)), 0)

    def test_internal_get_group_permissions(self):
        group = GroupFactory()
        group.permissions.add(self.permission)
        realm = RealmFactory(workspace=self.tenant)
        realm.groups.add(group)
        perms = self.backend._get_group_permissions(realm)
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission, perms)

    def test_internal_get_permission_user_not_active(self):
        user = UserFactory(is_active=False)
        realm = RealmFactory(user=user, workspace=self.tenant)
        perms = self.backend._get_permissions(realm, None, "realm")
        self.assertEqual(perms, set())

    def test_internal_get_permission_obj_not_none(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend._get_permissions(realm, realm, "realm")
        self.assertEqual(perms, set())

    def test_internal_get_permission_superuser(self):
        user = UserFactory(is_superuser=True)
        realm = RealmFactory(user=user, workspace=self.tenant)
        perms = self.backend._get_permissions(realm, None, "realm")
        self.assertEqual(len(perms), Permission.objects.count())

    def test_internal_get_permissions_realm_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend._get_permissions(realm, None, "realm")
        self.assertEqual(len(perms), 0)

    def test_internal_get_permissions_realm(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        perms = self.backend._get_permissions(realm, None, "realm")
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_internal_get_permissions_group_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend._get_permissions(realm, None, "group")
        self.assertEqual(len(perms), 0)

    def test_internal_get_permissions_group(self):
        group = GroupFactory()
        group.permissions.add(self.permission)
        realm = RealmFactory(workspace=self.tenant)
        realm.groups.add(group)
        perms = self.backend._get_permissions(realm, None, "group")
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_get_realm_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend.get_realm_permissions(realm, None)
        self.assertEqual(len(perms), 0)

    def test_get_permissions_realm(self):
        realm = RealmFactory(workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        perms = self.backend.get_realm_permissions(realm, None)
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_get_group_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend.get_group_permissions(realm, None)
        self.assertEqual(len(perms), 0)

    def test_get_group_permissions(self):
        group = GroupFactory()
        group.permissions.add(self.permission)
        realm = RealmFactory(workspace=self.tenant)
        realm.groups.add(group)
        perms = self.backend.get_group_permissions(realm, None)
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_get_all_permissions_empty(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend.get_all_permissions(realm)
        self.assertEqual(len(perms), 0)

    def test_get_all_permissions_user_not_active(self):
        user = UserFactory(is_active=False)
        realm = RealmFactory(user=user, workspace=self.tenant)
        perms = self.backend.get_all_permissions(realm)
        self.assertEqual(len(perms), 0)

    def test_get_all_permissions_obj_not_none(self):
        realm = RealmFactory(workspace=self.tenant)
        perms = self.backend.get_all_permissions(realm, realm)
        self.assertEqual(len(perms), 0)

    def test_get_all_permissions(self):
        group = GroupFactory()
        group.permissions.add(self.permission)
        realm = RealmFactory(workspace=self.tenant)
        realm.groups.add(group)
        realm.realm_permissions.add(self.permission)
        perms = self.backend.get_all_permissions(realm)
        self.assertEqual(len(perms), 1)
        self.assertIn(self.permission_label, perms)

    def test_has_perm_user_not_active(self):
        user = UserFactory(is_active=False)
        RealmFactory(user=user, workspace=self.tenant)
        self.assertFalse(self.backend.has_perm(user, self.permission.target))

    def test_has_perm_no_realm(self):
        user = UserFactory(is_active=False)
        self.assertFalse(self.backend.has_perm(user, self.permission.target))

    def test_has_perm_false(self):
        user = UserFactory()
        RealmFactory(user=user, workspace=self.tenant)
        self.assertFalse(self.backend.has_perm(user, self.permission.target))

    def test_has_perm(self):
        user = UserFactory()
        realm = RealmFactory(user=user, workspace=self.tenant)
        realm.realm_permissions.add(self.permission)
        self.assertTrue(self.backend.has_perm(user, self.permission.target))

    # def test_has_module_perms_user_not_active(self):
    #     user = UserFactory(is_active=False)
    #     realm = RealmFactory(user=user, workspace=self.tenant)
    #     perm = self.backend.has_module_perms(realm, self.permission_app_label)
    #     self.assertFalse(perm)

    # def test_has_module_perms_bad_label(self):
    #     realm = RealmFactory(workspace=self.tenant)
    #     realm.realm_permissions.add(self.permission)
    #     perm = self.backend.has_module_perms(realm, "wrong")
    #     self.assertFalse(perm)

    # def test_has_module_perms_false(self):
    #     realm = RealmFactory(workspace=self.tenant)
    #     perm = self.backend.has_module_perms(realm, self.permission_app_label)
    #     self.assertFalse(perm)

    # def test_has_module_perms(self):
    #     realm = RealmFactory(workspace=self.tenant)
    #     realm.realm_permissions.add(self.permission)
    #     perm = self.backend.has_module_perms(realm, self.permission_app_label)
    #     self.assertTrue(perm)
