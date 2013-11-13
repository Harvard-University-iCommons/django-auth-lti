from os.path import abspath, dirname, join, normpath
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

#from django.db.models import Q
#from icommons_common.models import *
from ims_lti_py.tool_provider import DjangoToolProvider

import gnupg
import base64
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LTIAuthBackend(ModelBackend):
    """
    This backend is to be used in conjunction with the ``PINAuthMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    # move this to config
    oauth_creds = {'test': 'secret'}

    # Create a User object if not already in the database?
    create_unknown_user = True

    def authenticate(self, request):

        request_key = request.POST.get('oauth_consumer_key', None)

        if request_key is None:
            logger.error("Request doesn't contain an oauth_consumer_key; can't continue.")
            raise PermissionDenied

        secret = oauth_creds.get(request_key, None)

        if secret is None:
            logger.error("Could not get a secret for key %s" % request_key)
            raise PermissionDenied

        tool_provider = DjangoToolProvider(request_key, secret, request.POST.dict())

        if not tool_provider.is_valid_request(request):
            logger.error("Invalid request: signature check failed.")
            raise PermissionDenied

        if time() - int(tool_provider.oauth_timestamp) > 60*60:
            logger.error("OAuth timestamp is too old.")
            raise PermissionDenied

        # (this is where we should check the nonce)

        # if we got this far, the user is good 

        user = None

        username = self.clean_username(request.POST.get('lis_person_sourcedid'))
        


        #logger.debug('authenticate using original/cleaned username: %s/%s' % (authen_userid,username))

        UserModel = get_user_model()

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
           
            user, created = UserModel.objects.get_or_create(**{
                UserModel.USERNAME_FIELD: username
            })

            if created:
                logger.debug('authenticate created a new user for %s' % username)
                user = self.configure_user(user)
            else:

                logger.debug('authenticate found an existing user for %s' % username)    
        else:
            logger.debug('automatic new user creation is turned OFF! just try to find and existing record')
            try:
                user = UserModel.objects.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                logger.debug('authenticate could not find user %s' % username)
                # should return some kind of error here?
                pass

        logger.debug('before configuring user')
        user = self.configure_user(user) 
        logger.debug('after configuring user')      

        return user

