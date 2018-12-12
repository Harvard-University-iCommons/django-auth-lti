
# django-auth-lti

django_auth_lti is a package that provides Django authentication middleware and backend classes for building tools that work with an LTI consumer. 

To use LTI authentication with a Django app, edit settings.py as follows:

* add 'django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware' to your MIDDLEWARE (Django >= 1.10) or MIDDLEWARE_CLASSES (Django < 1.10), making sure that it appears AFTER 'django.contrib.auth.middleware.AuthenticationMiddleware'

* add 'django_auth_lti.backends.LTIAuthBackend' to your BACKEND_CLASSES

* configure the OAuth credentials - add something like this to your project configuration:
```
LTI_OAUTH_CREDENTIALS = {
    'test': 'secret',
    'test2': 'reallysecret'
}
```

* OPTIONALLY, you can define a custom role key at the project level. Doing so will cause the middleware to look for any roles associated with that key during the launch request and merge them into the default LTI roles list.  You can declare such a key by adding this to your project configuration:
```
LTI_CUSTOM_ROLE_KEY = 'my-custom-role-key-change-me'
```

The MultiLTILaunchAuthMiddleware will ensure that all users of your app are authenticated before they can access any page.  Upon successful authentication, a Django user record is created (or updated) and the user is allowed to access the application.  The middleware will also make the LTI launch parameters available to any request via a 'LTI' parameter on the request object.
```
request.LTI.get('resource_link_id')
```
