from django.conf.urls import url

from demo.example.views import OrganizationListView

urlpatterns = [
    url(
        r'organization/$',
        OrganizationListView.as_view(),
        name='organization-list'
    ),
]
