from django.db import connection
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tenant_schemas.test.cases import TenantTestCase
from tenant_schemas.test.client import TenantClient
from tenant_schemas.utils import get_tenant_model

from tests.factories import UserFactory

TENANT_DOMAIN = 'tenant.example.com'
SCHEMA_NAME = 'test'


def create_tenant(domain, name):
    TenantModel = get_tenant_model()

    try:
        tenant = TenantModel.objects.get(
            domain_url=TENANT_DOMAIN,
            schema_name=SCHEMA_NAME,
        )
    except TenantModel.DoesNotExist:
        tenant = TenantModel(
            domain_url=TENANT_DOMAIN,
            schema_name=SCHEMA_NAME,
            name=SCHEMA_NAME,
        )
        tenant.save(verbosity=0)
    return tenant


class BaseTestCase(TenantTestCase):
    client_class = APIClient

    @classmethod
    def setUpClass(cls):
        cls.sync_shared()

        cls.tenant = create_tenant(TENANT_DOMAIN, SCHEMA_NAME)
        cls.tenant_other = create_tenant("other.example.com", "other")

        connection.set_tenant(cls.tenant)
        cls.cls_atomics = cls._enter_atomics()

    @classmethod
    def tearDownClass(cls):
        cls._rollback_atomics(cls.cls_atomics)
        connection.set_schema_to_public()

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.user_password = "123"
        self.user = UserFactory(password=self.user_password)

    def set_token(self, client, user):
        token = Token.objects.get(user__username=user.username)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
