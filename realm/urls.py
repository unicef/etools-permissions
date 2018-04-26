from django.conf.urls import url

from realm.views import SetRealmAPIView


urlpatterns = [
    url(r'^realm/set/$', SetRealmAPIView.as_view(), name='realm-set'),
]
