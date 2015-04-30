from django.core.exceptions import ImproperlyConfigured, PermissionDenied


def is_allowed(request, allowed_roles, raise_exception):
    # allowed_roles can either be a string (for just one)
    # or a tuple or list (for several)
    if not isinstance(allowed_roles, (list, tuple)):
        allowed = (allowed_roles, )
    else:
        allowed = allowed_roles
    
    lti_launch = request.session.get('LTI_LAUNCH', None)
    if not isinstance(lti_launch, dict):
        # If this is raised, then likely the project doesn't have
        # the correct settings or is being run outside of an lti context
        raise ImproperlyConfigured("No LTI_LAUNCH found in session")
    user_roles = lti_launch.get('roles', [])
    is_user_allowed = set(allowed) & set(user_roles)
    
    if not is_user_allowed and raise_exception:
        raise PermissionDenied
    
    return is_user_allowed


def has_lti_roles(request, roles):
    # TODO: Refactor this common code here and above to keep it DRY
    lti_launch = request.session.get('LTI_LAUNCH', None)
    if not isinstance(lti_launch, dict):
        # If this is raised, then likely the project doesn't have
        # the correct settings or is being run outside of an lti context
        raise ImproperlyConfigured("No LTI_LAUNCH found in session")
    user_roles = lti_launch.get('roles', [])
    return bool(set(user_roles) & set(roles))
