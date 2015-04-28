
from oauthlib.oauth1 import RequestValidator
from oauthlib.common import to_unicode
from django.conf import settings
from models import Nonce
import time

NONCE_TTL = 3600.0

class LTIRequestValidator(RequestValidator):

    enforce_ssl = False

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
        now = time.time()
        try:
            nonce_rec = Nonce.objects.get(nonce=nonce)
            last_seen = nonce_rec.timestamp
            if last_seen + NONCE_TTL < now:
                nonce_rec.timestamp = now
                nonce_rec.save()
                return True
            else:
                return False
        except Nonce.DoesNotExist:
            n = Nonce(nonce=nonce)
            n.save()
            return True

    def get_client_secret(self, client_key, request):
        secret = settings.LTI_OAUTH_CREDENTIALS.get(client_key, self.dummy_secret)
        # make sure secret val is unicode
        return to_unicode(secret)

