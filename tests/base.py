from django.db import connection
from tenant_schemas.test.cases import TenantTestCase
from tenant_schemas.test.client import TenantClient
from tenant_schemas.utils import get_tenant_model

from tests.factories import UserFactory

TENANT_DOMAIN = 'tenant.example.com'
SCHEMA_NAME = 'test'


class BaseTestCase(TenantTestCase):
    @classmethod
    def setUpClass(cls):
        cls.sync_shared()

        TenantModel = get_tenant_model()
        try:
            cls.tenant = TenantModel.objects.get(
                domain_url=TENANT_DOMAIN,
                schema_name=SCHEMA_NAME,
            )
        except TenantModel.DoesNotExist:
            cls.tenant = TenantModel(
                domain_url=TENANT_DOMAIN,
                schema_name=SCHEMA_NAME,
                name=SCHEMA_NAME,
            )
            cls.tenant.save(verbosity=0)

        connection.set_tenant(cls.tenant)
        cls.cls_atomics = cls._enter_atomics()

    @classmethod
    def tearDownClass(cls):
        cls._rollback_atomics(cls.cls_atomics)
        connection.set_schema_to_public()

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.user = UserFactory()
