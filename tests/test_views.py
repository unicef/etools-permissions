from django.core.urlresolvers import reverse
from rest_framework import status

from realm.models import Permission
from tests.base import BaseTestCase
from tests.factories import (
    OrganizationFactory,
    PermissionFactory,
    RealmFactory,
    UserFactory,
)


class TestIndexView(BaseTestCase):
    def test_get_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationListView(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('demo:organization-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationListAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="realm.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="example.organization.*"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(reverse('demo:organization-api-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse('demo:organization-api-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_permission(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.realm_permissions.add(self.permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('demo:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_workspace(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant_other,
        )
        realm.realm_permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('demo:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        realm = RealmFactory(
            user=self.user,
            organization=self.organization,
            workspace=self.tenant,
        )
        realm.realm_permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('demo:organization-api-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.organization.pk)


class TestOrganizationDetailAPIView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()
        self.permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_DISALLOW,
            target="realm.permission.*"
        )
        self.view_permission = PermissionFactory(
            permission=Permission.VIEW,
            permission_type=Permission.TYPE_ALLOW,
            target="example.organization.*"
        )

    def test_get_not_logged_in(self):
        response = self.client.get(
            reverse(
                'demo:organization-api-detail',
                args=[self.organization.pk]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_permission(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                'demo:organization-api-detail',
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
        realm.realm_permissions.add(self.permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'demo:organization-api-detail',
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
        realm.realm_permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'demo:organization-api-detail',
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
        realm.realm_permissions.add(self.view_permission)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                'demo:organization-api-detail',
                args=[self.organization.pk]
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.organization.pk)
