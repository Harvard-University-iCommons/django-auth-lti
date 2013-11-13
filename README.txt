=====
django-auth-lti
=====


django_auth_lti is a Django app that provides authentication middleware and backend for building tools that work with an LTI consumer. 

To use LTI authentication with a Django app, edit settings.py as follows:

- add 'icommons_common.auth.middleware.LTIAuthMiddleware' to your MIDDLEWARE_CLASSES, making sure that it appears AFTER 'django.contrib.auth.middleware.AuthenticationMiddleware'

The LTIAuthMiddleware will ensure that all users of your app are authenticated before they can access any page.  Upon successful authentication, a Django user record is created (or updated) and the user is allowed to access the application. 


