from django.views.generic import ListView
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveAPIView, ListAPIView

from demo.example.models import Organization
from demo.example.serializers import (
    OrganizationFieldLimitSerializer,
    OrganizationSerializer,
)
from etools_permissions.permissions import RealmPermission


class OrganizationListView(ListView):
    model = Organization


class OrganizationListAPIView(ListAPIView):
    queryset = Organization.objects.all()
    authentication_classes = (SessionAuthentication, )
    permission_classes = (RealmPermission, )
    serializer_class = OrganizationSerializer


class OrganizationDetailAPIView(RetrieveAPIView):
    queryset = Organization.objects.all()
    authentication_classes = (SessionAuthentication, )
    permission_classes = (RealmPermission, )
    serializer_class = OrganizationFieldLimitSerializer
