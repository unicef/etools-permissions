from django.views.generic import ListView
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

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


class OrganizationOpenListAPIView(OrganizationListAPIView):
    _ignore_permissions = True


class OrganizationQuerysetAPIView(APIView):
    queryset = Organization.objects.all()
    authentication_classes = (SessionAuthentication, )
    permission_classes = (RealmPermission, )

    def get(self, request, format=None):
        organizations = [o.name for o in self.queryset.all()]
        return Response(organizations)


class OrganizationGetQuerysetAPIView(APIView):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (RealmPermission, )

    def get_queryset(self):
        return Organization.objects.all()

    def get(self, request, format=None):
        organizations = [o.name for o in self.get_queryset()]
        return Response(organizations)


class OrganizationDetailAPIView(RetrieveAPIView):
    queryset = Organization.objects.all()
    authentication_classes = (SessionAuthentication, )
    permission_classes = (RealmPermission, )
    serializer_class = OrganizationFieldLimitSerializer
