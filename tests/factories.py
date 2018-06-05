from django.contrib.auth import get_user_model

import factory
from demo.organization.models import Organization
from demo.sample.models import Author, Book, ChildrensBook, Stats
from factory import fuzzy

from etools_permissions import models


class UserFactory(factory.django.DjangoModelFactory):
    username = fuzzy.FuzzyText()
    email = factory.Sequence(lambda n: "user{}@example.com".format(n))
    password = factory.PostGenerationMethodCall('set_password', '123')

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
    target = "etools_permissions.permission.*"

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


class AuthorFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=20)

    class Meta:
        model = Author


class BookFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=20)
    author = factory.SubFactory(AuthorFactory)
    previous = None

    class Meta:
        model = Book


class ChildrensBookFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=20)
    author = factory.SubFactory(AuthorFactory)
    max_age = fuzzy.FuzzyInteger(1, 10)
    previous = None

    class Meta:
        model = ChildrensBook


class StatsFactory(factory.django.DjangoModelFactory):
    approve = fuzzy.FuzzyInteger(0, 1000)
    disapprove = fuzzy.FuzzyInteger(0, 1000)
    book = factory.SubFactory(BookFactory)

    class Meta:
        model = Stats
