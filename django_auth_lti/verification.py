from django.core.exceptions import PermissionDenied, ImproperlyConfigured


def is_allowed(request, allowed_roles, raise_exception):
    if not hasattr(request, "LTI") or request.LTI is None:
        raise ImproperlyConfigured("Request is missing LTI attribute")

    if "roles" not in request.LTI:
        raise ImproperlyConfigured("LTI roles not found in request")

    if not isinstance(allowed_roles, (list, tuple)):
        allowed = (allowed_roles,)
    else:
        allowed = allowed_roles

    user_roles = request.LTI.get("roles", [])
    is_user_allowed = bool(set(allowed) & set(user_roles))

    if not is_user_allowed and raise_exception:
        raise PermissionDenied

    return is_user_allowed


def has_lti_roles(request, roles):
    if not hasattr(request, "LTI") or request.LTI is None:
        return False
    user_roles = request.LTI.get("roles", [])
    return bool(set(user_roles) & set(roles))
