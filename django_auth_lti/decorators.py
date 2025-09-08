from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse_lazy

from django_auth_lti.verification import is_allowed


def lti_role_required(allowed_roles, redirect_url=None, raise_exception=False):
    if redirect_url is None:
        redirect_url = reverse_lazy("not authorized")

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if is_allowed(request, allowed_roles, raise_exception):
                return view_func(request, *args, **kwargs)

            return redirect(redirect_url)

        return _wrapped_view

    return decorator
