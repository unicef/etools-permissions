from django.contrib.auth.models import User

import factory

from factory import fuzzy
from demo.example.models import Organization


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = 'test'


class OrganizationFactory(factory.Factory):
    class Meta:
        model = Organization

    name = fuzzy.FuzzyText(length=100)
