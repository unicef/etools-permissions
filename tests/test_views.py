from django.core.urlresolvers import reverse
from rest_framework import status

from tests.base import BaseTestCase


class TestIndexView(BaseTestCase):
    def test_get_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrganizationListView(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('demo:organization-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
