from django.http import HttpResponse
from django.contrib import auth

#from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
#from django.utils.functional import SimpleLazyObject
#from django.shortcuts import redirect
#from django.utils.http import urlquote

from icommons_common.models import *

import logging
logger = logging.getLogger(__name__)


class LTIAuthMiddleware(object):
    """
    Middleware for authenticating users via an LTI launch URL.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username and signature passed in the LTI launch post.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    """

    def process_request(self, request):
        logger.debug('inside process_request %s' % request.path )
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            logger.debug('improperly configured: requeset has no user attr')
            raise ImproperlyConfigured(
                "The Django PIN auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the PINAuthMiddleware class.")

        # if the user is already authenticated, just return
        if request.user.is_authenticated():
            # nothing more to do! 
            logger.debug('inside process_request: user is already authenticated: %s' % request.user)
            return

        else:
            # the request.user isn't authenticated!
            logger.debug('the request.user is not authenticated')
            #from pudb import set_trace; set_trace()


            # authenticate and log the user in
            user = auth.authenticate(request=request)

            if user:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.
                logger.debug('user was successfully authenticated; now log them in')
                request.user = user
                auth.login(request, user)
            else:
                # User could not be authenticated! Bail!
                logger.error('user could not be authenticated; bail with an error message')
                #return HttpResponse('Authentication error! Sorry!')
                raise PermissionDenied()


    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_str)
        try:
            logger.debug('calling the backend %s clean_username with %s' % (backend,username))
            username = backend.clean_username(username)
            logger.debug('cleaned username is %s' % username)
        except AttributeError:  # Backend has no clean_username method.
            pass
        return username
