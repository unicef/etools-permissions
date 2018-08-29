from demo.organization.models import Organization
from rest_framework import serializers

from etools_permissions.serializers import RealmSerializerMixin


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationFieldLimitSerializer(RealmSerializerMixin, OrganizationSerializer):
    """Fields are limited based on permissions of user"""
