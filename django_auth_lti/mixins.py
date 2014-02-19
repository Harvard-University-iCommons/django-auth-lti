from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from braces.views import LoginRequiredMixin


class LTIRoleRestrictionMixin(object):
    allowed_roles = None
    redirect_url = reverse_lazy('not_authorized')
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        if self.allowed_roles is None:
            raise ImproperlyConfigured(
                "'LTIRoleRestrictionMixin' requires "
                "'allowed_roles' attribute to be set.")

        # Handle allowed roles as either a list or a single string
        if not isinstance(self.allowed_roles, (list, tuple)):
            allowed = (self.allowed_roles, )
        else:
            allowed = self.allowed_roles

        lti_params = request.session.get('LTI_LAUNCH', None)
        user_roles = lti_params.get('roles', [])

        if set(allowed) & set(user_roles):
            return super(LTIRoleRestrictionMixin, self).dispatch(request, *args, **kwargs)

        if self.raise_exception:
            raise PermissionDenied

        return redirect(self.redirect_url)


class LTIRoleRequiredMixin(LoginRequiredMixin, LTIRoleRestrictionMixin):
    """
    Mixin is a shortcut to use both LoginRequiredMixin and LTIRoleRestrictionMixin
    """
    pass
