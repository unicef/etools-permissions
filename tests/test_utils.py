from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from demo.sample.models import Book, ChildrensBook, Stats
from etools_permissions import utils
from tests.base import BaseTestCase


class TestGetRealm(BaseTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_no_user(self):
        request = self.factory.post(
            reverse('organization:organization-api-list')
        )
        request.user = None
        self.assertIsNone(utils.get_realm(request))

    def test_anonymous_user(self):
        request = self.factory.post(
            reverse('organization:organization-api-list')
        )
        request.user = AnonymousUser()
        self.assertIsNone(utils.get_realm(request))


class TestCollectParentModels(BaseTestCase):
    def test_level_zero(self):
        result = utils.collect_parent_models(None, levels=0)
        self.assertEqual(result, [])


class TestCollectChildModels(BaseTestCase):
    def test_level_zero(self):
        result = utils.collect_child_models(None, levels=0)
        self.assertEqual(result, [])

    def test_no_child(self):
        result = utils.collect_child_models(Stats)
        self.assertEqual(result, [])

    def test_child(self):
        result = utils.collect_child_models(Book)
        self.assertEqual(result, [ChildrensBook])

    def test_child_levels(self):
        result = utils.collect_child_models(Book, levels=2)
        self.assertEqual(result, [ChildrensBook])
