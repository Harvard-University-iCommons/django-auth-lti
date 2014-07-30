from functools import wraps
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.utils.decorators import available_attrs
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy


def lti_role_required(allowed_roles, redirect_url=reverse_lazy('not_authorized'), raise_exception=False):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not isinstance(allowed_roles, (list, tuple)):
                allowed = (allowed_roles, )
            else:
                allowed = allowed_roles

            lti_params = request.session.get('LTI_LAUNCH', None)
            if lti_params is None:
                # If this is raised, then likely the project doesn't have
                # the correct settings or is being run outside of an lti context
                raise ImproperlyConfigured("No LTI_LAUNCH vale found in session")
            user_roles = lti_params.get('roles', [])
            if set(allowed) & set(user_roles):
                return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied

            return redirect(redirect_url)
        return _wrapped_view
    return decorator
