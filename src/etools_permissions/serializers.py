from rest_framework import serializers

from etools_permissions.models import Permission, Realm


class RealmSerializerMixin:
    """Limit fields shown based on which fields user is allowed to view/edit"""
    def _limit_fields_by_permission(self, fields, permission_type):
        valid_fields = list()
        for field in fields:
            field_target = "{}.{}".format(
                permission_type,
                Permission.get_target(self.Meta.model, field)
            )
            if self.context["request"].realm.has_perm(field_target):
                valid_fields.append(field)
        return valid_fields

    @property
    def _writable_fields(self):
        fields = super()._writable_fields
        return self._limit_fields_by_permission(fields, Permission.EDIT)

    @property
    def _readable_fields(self):
        fields = super()._readable_fields
        return self._limit_fields_by_permission(fields, Permission.VIEW)


class RealmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realm
        fields = "__all__"
