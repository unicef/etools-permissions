from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from demo.sample.models import Author, Book, ChildrensBook, Stats
from rest_framework.test import APIRequestFactory
from tests.base import BaseTestCase
from tests.factories import RealmFactory

from etools_permissions import utils


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


class TestSetRealm(BaseTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.post(
            reverse('organization:organization-api-list')
        )
        self.request.session = self.client.session
        self.realm = RealmFactory(workspace=self.tenant)

    def test_realm_none(self):
        self.request.realm = self.realm
        utils.set_realm(self.request, None)
        self.assertEqual(
            self.request.session[utils.SESSION_KEY],
            str(self.realm.pk)
        )
        self.assertEqual(self.request.realm, self.realm)

    def test_has_session(self):
        self.request.session[utils.SESSION_KEY] = str(self.realm.pk)
        utils.set_realm(self.request, self.realm)
        self.assertEqual(
            self.request.session[utils.SESSION_KEY],
            str(self.realm.pk)
        )
        # self.assertEqual(self.request.realm, self.realm)

    def test_has_different_session(self):
        self.request.session[utils.SESSION_KEY] = str(404)
        utils.set_realm(self.request, self.realm)
        self.assertEqual(
            self.request.session[utils.SESSION_KEY],
            str(self.realm.pk)
        )


class TestCollectParentModels(BaseTestCase):
    def test_level_zero(self):
        result = utils.collect_parent_models(None, levels=0)
        self.assertEqual(result, [])

    def test_no_parent(self):
        result = utils.collect_parent_models(Author)
        self.assertEqual(result, [])

    def test_parent(self):
        result = utils.collect_parent_models(ChildrensBook)
        self.assertEqual(result, [Book])

    def test_parent_levels(self):
        result = utils.collect_parent_models(ChildrensBook, levels=2)
        self.assertEqual(result, [Book])


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
