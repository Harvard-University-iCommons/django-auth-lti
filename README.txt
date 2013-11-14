=====
django-auth-lti
=====

django_auth_lti is a package that provides Django authentication middleware and backend classes for building tools that work with an LTI consumer. 

To use LTI authentication with a Django app, edit settings.py as follows:

- add 'django_auth_lti.middleware.LTIAuthMiddleware' to your MIDDLEWARE_CLASSES, making sure that it appears AFTER 'django.contrib.auth.middleware.AuthenticationMiddleware'

- add 'django_auth_lti.backends.LTIAuthBackend' to your BACKEND_CLASSES

- configure the OAuth credentials - add something like this to your project configuration:

OAUTH_CREDENTIALS = {
    'test': 'secret',
    'test2': 'reallysecret'
}

The LTIAuthMiddleware will ensure that all users of your app are authenticated before they can access any page.  Upon successful authentication, a Django user record is created (or updated) and the user is allowed to access the application. 


