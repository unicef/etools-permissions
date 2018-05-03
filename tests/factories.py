from django.contrib.auth import get_user_model

import factory

from factory import fuzzy

from demo.example.models import Organization
from realm import models


class UserFactory(factory.django.DjangoModelFactory):
    username = fuzzy.FuzzyText(length=100)

    class Meta:
        model = get_user_model()


class OrganizationFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=100)

    class Meta:
        model = Organization


class PermissionFactory(factory.django.DjangoModelFactory):
    permission = fuzzy.FuzzyChoice(
        [x[0] for x in models.Permission.PERMISSION_CHOICES]
    )
    permission_type = fuzzy.FuzzyChoice(
        [x[0] for x in models.Permission.TYPE_CHOICES]
    )
    target = "realm.permission.*"

    class Meta:
        model = models.Permission


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group


class RealmFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)

    class Meta:
        model = models.Realm
