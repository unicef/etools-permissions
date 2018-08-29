from django.conf.urls import include, url
from django.contrib import admin

from demo.organization.urls import urlpatterns as organization_patterns
from demo.tenant.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(
        r'^organization/',
        include(
            (organization_patterns, 'organization'),
            namespace='organization'
        )
    ),
]
