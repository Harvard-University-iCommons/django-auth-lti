import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from oauthlib.common import to_unicode
from oauthlib.oauth1 import RequestValidator

logger = logging.getLogger(__name__)
NONCE_TTL = 3600 * 6


class LTIRequestValidator(RequestValidator):

    enforce_ssl = True
    allowed_signature_methods = ['HMAC-SHA1']
    timestamp_lifetime = NONCE_TTL

    #TODO: Find out if this is used...
    dummy_secret = 'secret'
    dummy_client = (u'dummy_'
        '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')

    def check_client_key(self, key):
        # any non-empty string is OK as a client key
        return len(key) > 0

    def check_nonce(self, nonce):
        # any non-empty string is OK as a nonce
        return len(nonce) > 0

    def validate_client_key(self, client_key, request):
        return client_key in settings.LTI_OAUTH_CREDENTIALS

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                                     request, request_token=None,
                                     access_token=None):
        nonce_key = 'lti_nonce:{}-{}-{}-{}'.format(client_key, timestamp, nonce, request_token or access_token)
        exists = cache.get(nonce_key)
        if exists:
            logger.debug("nonce already exists: %s", nonce)
            return False
        else:
            logger.debug("unused nonce, storing: %s", nonce)
            cache.set(nonce_key, nonce, NONCE_TTL)
            return True

    def get_client_secret(self, client_key, request):
        secret = settings.LTI_OAUTH_CREDENTIALS.get(client_key, self.dummy_secret)
        # make sure secret val is unicode
        return to_unicode(secret)
