from django.db import models

from tenant_schemas.models import TenantMixin


class Workspace(TenantMixin):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
