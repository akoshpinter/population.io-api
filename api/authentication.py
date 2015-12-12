from rest_framework import authentication
from rest_framework import exceptions
from api.datastore import using_tokens, valid_token

class CustomTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom implementation of token verification. This is only a partial implementation of Django REST frameworks
    authentication module. This implementation throws an exception and returns 401 HTTP status with the
    'WWW-Authenticate' header if there was no valid token specified in the header. Does not use Django's
    authentication models that require a database.
    """

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not using_tokens(): # we skip authentication if tokens are not loaded
            return None

        if not auth or auth[0].lower() != b'token':
            msg = 'Token header is not provided.'
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        if not valid_token(auth[1]):
            msg = 'Invalid token provided.'
            raise exceptions.AuthenticationFailed(msg)

        # We have authenticated the user, but we are returning like no authentication was done
        # because Djangos user model requires use of database
        return None

    def authenticate_header(self, request):
        return 'Token'
