from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

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


class RealmFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)

    class Meta:
        model = models.Realm


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group


class PermissionFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText()
    content_type = ContentType.objects.first()
    codename = fuzzy.FuzzyText()

    class Meta:
        model = Permission
