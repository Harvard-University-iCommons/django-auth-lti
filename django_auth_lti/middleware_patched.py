import logging

import django.urls
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse as django_reverse
from django.utils.deprecation import MiddlewareMixin

from django_auth_lti.thread_local import get_current_request

from .conf import get_excluded_paths
from .thread_local import set_current_request
from .timer import Timer

# importing here will ensure that django.urls.reverse is patched
# for other libraries and parts of django, e.g. `url` template tag,
# when the middleware is loaded

logger = logging.getLogger(__name__)


class MultiLTILaunchAuthMiddleware(MiddlewareMixin):
    """
    Middleware for authenticating users via an LTI launch URL.

    If the request is an LTI launch request, then this middleware attempts to
    authenticate the username and signature passed in the POST data.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    The LTI launch parameter dict is stored in the session keyed with the
    resource_link_id to uniquely identify LTI launches of the LTI producer.
    The LTI launch parameter dict is also set as the 'LTI' attribute on the
    current request object to simplify access to the parameters.

    The current request object is set as a thread local attribute so that the
    monkey-patching of django's reverse() function (see ./__init__.py) can access
    it in order to retrieve the current resource_link_id.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        logger.debug("inside process_request %s", getattr(request, "path", ""))

        # Skip on excluded paths but still expose request to thread-local
        if getattr(request, "path", "") in get_excluded_paths():
            set_current_request(request)
            return

        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, "user"):
            logger.debug("improperly configured: request has no user attr")
            raise ImproperlyConfigured(
                "The Django LTI auth middleware requires the authentication middleware "
                "to be installed. Edit your MIDDLEWARE setting to include "
                "'django.contrib.auth.middleware.AuthenticationMiddleware' "
                "before the LTI middleware."
            )

        from django_auth_lti import middleware as _mw

        resource_link_id = None
        is_launch = (
            request.method == "POST"
            and request.POST.get("lti_message_type") == "basic-lti-launch-request"
        )

        if is_launch:
            logger.debug("received a basic-lti-launch-request")

            # If a user is already authenticated on the request, trust it.
            # Otherwise fall back to auth.authenticate/login.
            user = request.user if getattr(request.user, "is_authenticated", False) else None
            if user is None:
                logger.debug("authenticating the user via LTI params")
                with Timer() as t:
                    user = _mw.auth.authenticate(request=request)
                logger.debug("authenticate() took %s s", t.secs)

            if user is not None:
                # Only call login if we authenticated just now (avoids needing a real session in tests)
                if not getattr(request.user, "is_authenticated", False):
                    logger.debug("logging user in to persist session")
                    request.user = user
                    with Timer() as t:
                        _mw.auth.login(request, user)
                    logger.debug("login() took %s s", t.secs)
                else:
                    # Ensure request.user is our authenticated user object
                    request.user = user

                resource_link_id = request.POST.get("resource_link_id")

                lti_launch = {
                    "context_id": request.POST.get("context_id"),
                    "context_label": request.POST.get("context_label"),
                    "context_title": request.POST.get("context_title"),
                    "context_type": request.POST.get("context_type"),
                    "custom_brand_config_js": request.POST.get("custom_brand_config_js"),
                    "custom_canvas_account_id": request.POST.get("custom_canvas_account_id"),
                    "custom_canvas_account_sis_id": request.POST.get(
                        "custom_canvas_account_sis_id"
                    ),
                    "custom_canvas_api_domain": request.POST.get("custom_canvas_api_domain"),
                    "custom_canvas_course_id": request.POST.get("custom_canvas_course_id"),
                    "custom_canvas_course_sectionsissourceids": request.POST.get(
                        "custom_canvas_course_sectionsissourceids", ""
                    ).split(","),
                    "custom_canvas_css_common": request.POST.get("custom_canvas_css_common"),
                    "custom_canvas_enrollment_state": request.POST.get(
                        "custom_canvas_enrollment_state"
                    ),
                    "custom_canvas_membership_roles": request.POST.get(
                        "custom_canvas_membership_roles", ""
                    ).split(","),
                    "custom_canvas_person_email_sis": request.POST.get(
                        "custom_canvas_person_email_sis"
                    ),
                    "custom_canvas_term_name": request.POST.get("custom_canvas_term_name"),
                    "custom_canvas_user_id": request.POST.get("custom_canvas_user_id"),
                    "custom_canvas_user_login_id": request.POST.get("custom_canvas_user_login_id"),
                    "launch_presentation_css_url": request.POST.get("launch_presentation_css_url"),
                    "launch_presentation_document_target": request.POST.get(
                        "launch_presentation_document_target"
                    ),
                    "launch_presentation_height": request.POST.get("launch_presentation_height"),
                    "launch_presentation_locale": request.POST.get("launch_presentation_locale"),
                    "launch_presentation_return_url": request.POST.get(
                        "launch_presentation_return_url"
                    ),
                    "launch_presentation_width": request.POST.get("launch_presentation_width"),
                    "lis_course_offering_sourcedid": request.POST.get(
                        "lis_course_offering_sourcedid"
                    ),
                    "lis_outcome_service_url": request.POST.get("lis_outcome_service_url"),
                    "lis_person_contact_email_primary": request.POST.get(
                        "lis_person_contact_email_primary"
                    ),
                    "lis_person_name_family": request.POST.get("lis_person_name_family"),
                    "lis_person_name_full": request.POST.get("lis_person_name_full"),
                    "lis_person_name_given": request.POST.get("lis_person_name_given"),
                    "lis_person_sourcedid": request.POST.get("lis_person_sourcedid"),
                    "lti_message_type": request.POST.get("lti_message_type"),
                    "resource_link_description": request.POST.get("resource_link_description"),
                    "resource_link_id": resource_link_id,
                    "resource_link_title": request.POST.get("resource_link_title"),
                    "roles": request.POST.get("roles", "").split(","),
                    "selection_directive": request.POST.get("selection_directive"),
                    "tool_consumer_info_product_family_code": request.POST.get(
                        "tool_consumer_info_product_family_code"
                    ),
                    "tool_consumer_info_version": request.POST.get("tool_consumer_info_version"),
                    "tool_consumer_instance_contact_email": request.POST.get(
                        "tool_consumer_instance_contact_email"
                    ),
                    "tool_consumer_instance_description": request.POST.get(
                        "tool_consumer_instance_description"
                    ),
                    "tool_consumer_instance_guid": request.POST.get("tool_consumer_instance_guid"),
                    "tool_consumer_instance_name": request.POST.get("tool_consumer_instance_name"),
                    "tool_consumer_instance_url": request.POST.get("tool_consumer_instance_url"),
                    "user_id": request.POST.get("user_id"),
                    "user_image": request.POST.get("user_image"),
                }

                # Merge custom roles if configured
                if hasattr(_mw.settings, "LTI_CUSTOM_ROLE_KEY"):
                    custom_roles = request.POST.get(_mw.settings.LTI_CUSTOM_ROLE_KEY, "").split(",")
                    lti_launch["roles"] += [r for r in custom_roles if r]

                # Use dict-like session (works for tests where request.session is just `{}`)
                lti_launches = request.session.get("LTI_LAUNCH")
                if not lti_launches:
                    lti_launches = {}
                    request.session["LTI_LAUNCH"] = lti_launches

                # Index launches
                lti_launch_count = request.session.get("LTI_LAUNCH_COUNT", 0) + 1
                request.session["LTI_LAUNCH_COUNT"] = lti_launch_count
                lti_launch["_order"] = lti_launch_count

                # Enforce max launches (FIFO unless re-launching same resource)
                max_launches = getattr(_mw.settings, "LTI_AUTH_MAX_LAUNCHES", 10)
                logger.info(
                    "LTI launch count %s [max=%s]",
                    len(list(lti_launches.keys())),
                    max_launches,
                )
                if len(list(lti_launches.keys())) >= max_launches:
                    remove_resource_link_id = resource_link_id
                    if remove_resource_link_id not in lti_launches:
                        ordered = sorted(
                            lti_launches.items(),
                            key=lambda item: item[1].get("_order", -1),
                        )
                        remove_resource_link_id = ordered[0][0]
                    invalidated = lti_launches.pop(remove_resource_link_id)
                    logger.info("LTI launch invalidated: %s", invalidated)

                lti_launches[resource_link_id] = lti_launch
                logger.info("LTI launch added to session: %s", lti_launch)

            else:
                logger.warning(
                    "user could not be authenticated via LTI params; let the request continue "
                    "in case another auth plugin is configured"
                )
        else:
            # Non-launch requests: read resource_link_id from query string
            resource_link_id = request.GET.get("resource_link_id")

        # Expose current launch on the request and stash request in thread-local
        request.LTI = request.session.get("LTI_LAUNCH", {}).get(resource_link_id, {})
        set_current_request(request)

        if not request.LTI:
            logger.warning("Could not find LTI launch for resource_link_id %s", resource_link_id)

    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_str)
        try:
            logger.debug("calling the backend %s clean_username with %s", backend, username)
            username = backend.clean_username(username)
            logger.debug("cleaned username is %s", username)
        except AttributeError:  # Backend has no clean_username method.
            pass
        return username


def lti_reverse(
    viewname,
    urlconf=None,
    args=None,
    kwargs=None,
    current_app=None,
    exclude_resource_link_id=False,
):
    """Wrapper around django.urls.reverse that appends resource_link_id if available."""
    url = django_reverse(
        viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app
    )

    if exclude_resource_link_id:
        return url

    request = get_current_request()
    if request and hasattr(request, "LTI"):
        resource_link_id = request.LTI.get("resource_link_id")
        if resource_link_id:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}resource_link_id={resource_link_id}"
    return url


django.urls.reverse = lti_reverse
