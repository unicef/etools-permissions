from rest_framework import serializers

from etools_permissions.models import Realm


class RealmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realm
        fields = "__all__"
