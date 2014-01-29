from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class GroupMembershipRequiredMixin(LoginRequiredMixin):
    allowed_groups = None
    redirect_url = reverse_lazy('not_authorized')
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        if self.allowed_groups is None:
            raise ImproperlyConfigured(
                "'GroupMembershipRequiredMixin' requires "
                "'allowed_groups' attribute to be set.")
        if not isinstance(self.allowed_groups, (list, tuple)):
            allowed = (self.allowed_groups, )
        else:
            allowed = self.allowed_groups

        group_ids = request.session.get('USER_GROUPS', [])
        if set(allowed) & set(group_ids):
            return super(GroupMembershipRequiredMixin, self).dispatch(request, *args, **kwargs)

        if self.raise_exception:
            raise PermissionDenied

        return redirect(self.redirect_url)
