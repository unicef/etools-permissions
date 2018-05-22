from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject


def get_realm(request):
    from etools_permissions.utils import get_realm
    if not hasattr(request, '_cached_realm'):
        request._cached_realm = get_realm(request)
    return request._cached_realm


class RealmAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
            "The Realm Auth middleware requires Django Authentication "
            "middleware to be installed. Edit your MIDDLEWARE%s setting to"
            "insert 'django.contrib.auth.middleware.AuthenticationMiddleware' "
            "before 'auth.middleware.RealmAuthMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        request.realm = SimpleLazyObject(lambda: get_realm(request))
