from django.conf.urls import url

from demo.organization import views

urlpatterns = [
    url(
        r'^/$',
        views.OrganizationListView.as_view(),
        name='organization-list'
    ),
    url(
        r'^api/organization/$',
        views.OrganizationListAPIView.as_view(),
        name='organization-api-list'
    ),
    url(
        r'^api/organization/open/$',
        views.OrganizationOpenListAPIView.as_view(),
        name='organization-api-list-open'
    ),
    url(
        r'^api/organization/queryset/$',
        views.OrganizationQuerysetAPIView.as_view(),
        name='organization-api-list-queryset'
    ),
    url(
        r'^api/organization/getqueryset/$',
        views.OrganizationGetQuerysetAPIView.as_view(),
        name='organization-api-list-getqueryset'
    ),
    url(
        r'^api/organization/(?P<pk>\d+)/$',
        views.OrganizationDetailAPIView.as_view(),
        name='organization-api-detail'
    ),
]
