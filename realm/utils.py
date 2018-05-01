from django.utils.crypto import constant_time_compare

from realm.models import Realm

SESSION_KEY = '_auth_realm_id'
HASH_SESSION_KEY = '_auth_realm_hash'


def _get_realm_session_key(request):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return Realm._meta.pk.to_python(request.session[SESSION_KEY])


def get_realm(request):
    """
    Return the realm model instance associated with the given request session.
    If no realm is retrieved, return an instance of `AnonymousUser`.
    """
    realm = None
    if request.user is not None:
        try:
            realm = Realm.objects.get(user__pk=request.user.pk)
        except Realm.DoesNotExist:
            pass

    return realm


def set_realm(request, realm):
    """
    Persist a realm id in the request. This way a realm doesn't
    have to set on every request.
    """
    session_auth_hash = ''
    if realm is None:
        realm = request.realm
    if hasattr(realm, 'get_session_auth_hash'):
        session_auth_hash = realm.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_realm_session_key(request) != realm.user.pk or (
                session_auth_hash and not constant_time_compare(
                    request.session.get(HASH_SESSION_KEY, ''),
                    session_auth_hash
                )
        ):
            # To avoid reusing another realm's session, create a new, empty
            # session if the existing session corresponds to a different realm.
            request.session.flush()
    else:
        request.session.cycle_key()

    request.session[SESSION_KEY] = Realm._meta.pk.value_to_string(realm)
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'realm'):
        request.realm = realm
