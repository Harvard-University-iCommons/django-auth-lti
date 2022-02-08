
# django-auth-lti

django_auth_lti is a package that provides Django authentication middleware and backend classes for building tools that work with an LTI consumer.

To use LTI authentication with a Django app, edit settings.py as follows:

* add `django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware` to your MIDDLEWARE (Django >= 1.10), making sure that it appears AFTER `django.contrib.auth.middleware.AuthenticationMiddleware`

* add 'django_auth_lti.backends.LTIAuthBackend' to your `BACKEND_CLASSES`

* configure the OAuth credentials - add something like this to your project configuration:
```python
LTI_OAUTH_CREDENTIALS = {
    'test': 'secret',
    'test2': 'reallysecret'
}
```

* OPTIONALLY, you can define a custom role key at the project level. Doing so will cause the middleware to look for any roles associated with that key during the launch request and merge them into the default LTI roles list.  You can declare such a key by adding this to your project configuration:
```python
LTI_CUSTOM_ROLE_KEY = 'my-custom-role-key-change-me'
```

The `MultiLTILaunchAuthMiddleware` will ensure that all users of your app are authenticated before they can access any page.  Upon successful authentication, a Django user record is created (or updated) and the user is allowed to access the application.  The middleware will also make the LTI launch parameters available to any request via a 'LTI' parameter on the request object.
```python
request.LTI.get('resource_link_id')
```

# Excluding paths

The middleware and reverse monkeypatch will skip checks for the `LTI` parameter if:

* `request.path` is blank (i.e. the empty string `""`)
* `request.path` exactly matches one of the paths in the `EXCLUDE_PATHS` setting.

To provide custom paths to exclude (e.g. `/w/ping/` for watchman, or `/app/tool_config/`), add the following in your django project condfiguration:

```python
DJANGO_AUTH_LTI_EXCLUDE_PATHS = [
    '/lti_tool/tool_config/',
    '/w/ping/',
]
```

# Local development

Bootstrapping a local Python development environment on your host machine for testing (`USE_PYTHON_VERSION` can correspond to the Python version under test):

```sh
USE_PYTHON_VERSION="3.9.10"
VENV_DIR=".venv"
pyenv install --skip-existing ${USE_PYTHON_VERSION}
rm -Rf "${VENV_DIR}" && PYENV_VERSION=${USE_PYTHON_VERSION} python -m venv "${VENV_DIR}"
. "${VENV_DIR}"/bin/activate && pip install --upgrade pip wheel
. "${VENV_DIR}"/bin/activate && python setup.py install
```

To test against a specific version of Django, you can `pip install` it before running `python setup.py install`.

# Testing

To run tests in a single environment:

```sh
python run_tests.py
```

To run a test matrix across Python and Django versions:

```sh
pip install tox

# You'll need to have all the Python versions specified in tox installed.
# For pyenv, you can use e.g.
#
#    pyenv install --skip-existing 3.7.x
#    pyenv install --skip-existing 3.8.x
#    pyenv install --skip-existing 3.9.x
#    pyenv install --skip-existing 3.10.x
#
# ... where x is the specific version available to you in pyenv.
# Then make them available to tox like so:
#
#    pyenv local 3.7.x 3.8.x 3.9.x 3.10.x

tox  # --parallel (optional)
```
