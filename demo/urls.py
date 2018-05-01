from django.conf.urls import url, include
from django.contrib import admin

from demo.example.urls import urlpatterns as demo_patterns
from demo.tenant.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^demo/', include(demo_patterns, namespace='demo')),
]
