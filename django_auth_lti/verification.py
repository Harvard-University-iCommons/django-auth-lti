from django.core.exceptions import ImproperlyConfigured, PermissionDenied

def is_allowed(request, allowed_roles, raise_exception):
    # allowed_roles can either be a string (for just one)
    # or a tuple or list (for several)
    if not isinstance(allowed_roles, (list, tuple)):
        allowed = (allowed_roles, )
    else:
        allowed = allowed_roles
    
    if ("LTI_LAUNCH" not in request.session
        or request.session["LTI_LAUNCH"] is None):
        # If this is raised, then likely the project doesn't have
        # the correct settings or is being run outside of an lti context
        raise ImproperlyConfigured("No LTI_LAUNCH vale found in session")
    user_roles = request.session['LTI_LAUNCH'].get('roles', [])
    is_user_allowed =  set(allowed) & set(user_roles)
    
    if not is_user_allowed and raise_exception:
        raise PermissionDenied
    
    return is_user_allowed
