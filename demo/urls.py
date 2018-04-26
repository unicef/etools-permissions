from django.conf.urls import url, include
from django.contrib import admin

from demo.example.urls import urlpatterns as demopatterns
from demo.tenant.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^demo/', include(demopatterns, namespace='demo')),
]
