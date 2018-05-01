from django.conf.urls import url

from demo.example.views import (
    OrganizationDetailAPIView,
    OrganizationListView,
    OrganizationListAPIView,
)

urlpatterns = [
    url(
        r'^organization/$',
        OrganizationListView.as_view(),
        name='organization-list'
    ),
     url(
        r'^api/organization/$',
        OrganizationListAPIView.as_view(),
        name='organization-api-list'
    ),
     url(
        r'^api/organization/(?P<pk>\d+)/$',
        OrganizationDetailAPIView.as_view(),
        name='organization-api-detail'
    ),
]
