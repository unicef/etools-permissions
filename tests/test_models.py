from realm.models import Realm
from tests.base import SCHEMA_NAME, BaseTestCase
from tests.factories import OrganizationFactory


class TestRealm(BaseTestCase):
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
