from django.urls import reverse

from rest_framework import status
from tests.base import BaseTestCase
from tests.factories import OrganizationFactory, PermissionFactory, RealmFactory, UserFactory

from etools_permissions.models import Permission


class TestIndexView(BaseTestCase):
    def test_get_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationListView(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('organization:organization-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationListAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="etools_permissions.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.*"
        )
        self.view_field_id_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.id"
        )
        self.view_field_name_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.name"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(reverse('organization:organization-api-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse('organization:organization-api-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_permission(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_workspace(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant_other,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.organization.pk)

    def test_get_permission_field(self):
        """If not using realm serializer mixin, then permissions on all fields
        is required for user to have permissions to view.
        """
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_field_id_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_permission_field_all(self):
        """If not using realm serializer mixin, then permissions on all fields
        is required for user to have permissions to view.
        """
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_field_id_permission)
        realm.permissions.add(self.view_field_name_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.organization.pk)
        self.assertEqual(response.data[0]["name"], self.organization.name)


class TestOrganizationOpenListAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()

    def test_get_not_logged_in(self):
        response = self.client.get(reverse('organization:organization-api-list-open'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse('organization:organization-api-list-open'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationQuerysetAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization_1 = OrganizationFactory(name="Org 1")
        self.organization_2 = OrganizationFactory(name="Org 2")
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="etools_permissions.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.*"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(
            reverse('organization:organization-api-list-queryset')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse('organization:organization-api-list-queryset')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization_1,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list-queryset'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class TestOrganizationGetQuerysetAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization_1 = OrganizationFactory(name="Org 1")
        self.organization_2 = OrganizationFactory(name="Org 2")
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="etools_permissions.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.*"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(
            reverse('organization:organization-api-list-getqueryset')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse('organization:organization-api-list-getqueryset')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization_1,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('organization:organization-api-list-getqueryset'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class TestOrganizationDetailAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="etools_permissions.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.*"
        )
        self.view_field_id_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.id"
        )
        self.view_field_name_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="organization.organization.name"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_permission(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_workspace(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant_other,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.organization.pk)

    def test_get_permission_field(self):
        """If using realm serializer mixin, then permissions on all fields
        is not required for user to have permissions to view.
        """
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_field_name_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.organization.name)
        self.assertNotIn("id", response.data.keys())

    def test_get_permission_field_all(self):
        """If using realm serializer mixin, then permissions on all fields
        is not required for user to have permissions to view.
        """
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.permissions.add(self.view_field_id_permission)
        realm.permissions.add(self.view_field_name_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'organization:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.organization.pk)
        self.assertEqual(response.data["name"], self.organization.name)
