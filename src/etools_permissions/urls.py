from django.conf.urls import url

from etools_permissions.views import SetRealmAPIView

urlpatterns = [
    url(r'^realm/set/$', SetRealmAPIView.as_view(), name='realm-set'),
]
