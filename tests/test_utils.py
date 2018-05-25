from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from etools_permissions import utils
from tests.base import BaseTestCase


class TestGetRealm(BaseTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_no_user(self):
        request = self.factory.post(reverse('demo:organization-api-list'))
        request.user = None
        self.assertIsNone(utils.get_realm(request))

    def test_anonymous_user(self):
        request = self.factory.post(reverse('demo:organization-api-list'))
        request.user = AnonymousUser()
        self.assertIsNone(utils.get_realm(request))
