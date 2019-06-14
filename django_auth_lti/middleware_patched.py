import logging

import django_auth_lti.patch_reverse

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .timer import Timer

from .thread_local import set_current_request

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # Django < 1.10
    MiddlewareMixin = object


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

    def process_request(self, request):
        logger.debug('inside process_request %s' % request.path)

        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            logger.debug('improperly configured: request has no user attr')
            raise ImproperlyConfigured(
                "The Django LTI auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the PINAuthMiddleware class.")

        resource_link_id = None
        if request.method == 'POST' and request.POST.get('lti_message_type') == 'basic-lti-launch-request':
            logger.debug('received a basic-lti-launch-request - authenticating the user')

            # authenticate and log the user in
            with Timer() as t:
                user = auth.authenticate(request=request)
            logger.debug('authenticate() took %s s' % t.secs)

            if user is not None:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.

                logger.debug('user was successfully authenticated; now log them in')
                request.user = user
                with Timer() as t:
                    auth.login(request, user)

                logger.debug('login() took %s s' % t.secs)

                resource_link_id = request.POST.get('resource_link_id', None)
                lti_launch = {
                    'context_id': request.POST.get('context_id', None),
                    'context_label': request.POST.get('context_label', None),
                    'context_title': request.POST.get('context_title', None),
                    'context_type': request.POST.get('context_type', None),
                    'custom_canvas_account_id': request.POST.get('custom_canvas_account_id', None),
                    'custom_canvas_account_sis_id': request.POST.get('custom_canvas_account_sis_id', None),
                    'custom_canvas_api_domain': request.POST.get('custom_canvas_api_domain', None),
                    'custom_canvas_course_id': request.POST.get('custom_canvas_course_id', None),
                    'custom_canvas_enrollment_state': request.POST.get('custom_canvas_enrollment_state', None),
                    'custom_canvas_membership_roles': request.POST.get('custom_canvas_membership_roles', '').split(','),
                    'custom_canvas_user_id': request.POST.get('custom_canvas_user_id', None),
                    'custom_canvas_user_login_id': request.POST.get('custom_canvas_user_login_id', None),
                    'launch_presentation_css_url': request.POST.get('launch_presentation_css_url', None),
                    'launch_presentation_document_target': request.POST.get('launch_presentation_document_target', None),
                    'launch_presentation_height': request.POST.get('launch_presentation_height', None),
                    'launch_presentation_locale': request.POST.get('launch_presentation_locale', None),
                    'launch_presentation_return_url': request.POST.get('launch_presentation_return_url', None),
                    'launch_presentation_width': request.POST.get('launch_presentation_width', None),
                    'lis_course_offering_sourcedid': request.POST.get('lis_course_offering_sourcedid', None),
                    'lis_outcome_service_url': request.POST.get('lis_outcome_service_url', None),
                    'lis_person_contact_email_primary': request.POST.get('lis_person_contact_email_primary', None),
                    'lis_person_name_family': request.POST.get('lis_person_name_family', None),
                    'lis_person_name_full': request.POST.get('lis_person_name_full', None),
                    'lis_person_name_given': request.POST.get('lis_person_name_given', None),
                    'lis_person_sourcedid': request.POST.get('lis_person_sourcedid', None),
                    'lti_message_type': request.POST.get('lti_message_type', None),
                    'resource_link_description': request.POST.get('resource_link_description', None),
                    'resource_link_id': resource_link_id,
                    'resource_link_title': request.POST.get('resource_link_title', None),
                    'roles': request.POST.get('roles', '').split(','),
                    'selection_directive': request.POST.get('selection_directive', None),
                    'tool_consumer_info_product_family_code': request.POST.get('tool_consumer_info_product_family_code', None),
                    'tool_consumer_info_version': request.POST.get('tool_consumer_info_version', None),
                    'tool_consumer_instance_contact_email': request.POST.get('tool_consumer_instance_contact_email', None),
                    'tool_consumer_instance_description': request.POST.get('tool_consumer_instance_description', None),
                    'tool_consumer_instance_guid': request.POST.get('tool_consumer_instance_guid', None),
                    'tool_consumer_instance_name': request.POST.get('tool_consumer_instance_name', None),
                    'tool_consumer_instance_url': request.POST.get('tool_consumer_instance_url', None),
                    'user_id': request.POST.get('user_id', None),
                    'user_image': request.POST.get('user_image', None),
                }
                # If a custom role key is defined in project, merge into existing role list
                if hasattr(settings, 'LTI_CUSTOM_ROLE_KEY'):
                    custom_roles = request.POST.get(settings.LTI_CUSTOM_ROLE_KEY, '').split(',')
                    lti_launch['roles'] += [_f for _f in custom_roles if _f]  # Filter out any empty roles

                lti_launches = request.session.get('LTI_LAUNCH')
                if not lti_launches:
                    lti_launches = {}
                    request.session['LTI_LAUNCH'] = lti_launches

                # Count the LTI launches and index each one so they can be ordered.
                # We are not using an OrderedDict because django serializes using JSON by default, which would
                # require a custom serializer to ensure objects are deserialized appropriately
                lti_launch_count = request.session.get('LTI_LAUNCH_COUNT', 0) + 1
                request.session['LTI_LAUNCH_COUNT'] = lti_launch_count
                lti_launch['_order'] = lti_launch_count

                # Limit the number of LTI launches stored in the session
                max_launches = getattr(settings, 'LTI_AUTH_MAX_LAUNCHES', 10)
                logger.info("LTI launch count %s [max=%s]" % (len(list(lti_launches.keys())), max_launches))
                if len(list(lti_launches.keys())) >= max_launches:
                    # If the current resource is being re-launched, then we should just invalidate the old launch,
                    # otherwise we should evict the oldest launch (FIFO).
                    remove_resource_link_id = resource_link_id
                    if remove_resource_link_id not in lti_launches:
                        ordered_launches = sorted(list(lti_launches.items()), key=lambda item: item[1].get('_order', -1))
                        remove_resource_link_id = ordered_launches[0][0]
                    invalidated_launch = lti_launches.pop(remove_resource_link_id)
                    logger.info("LTI launch invalidated: %s", invalidated_launch)

                lti_launches[resource_link_id] = lti_launch
                logger.info("LTI launch added to session: %s", lti_launch)
            else:
                # User could not be authenticated!
                logger.warning('user could not be authenticated via LTI params; let the request continue in case another auth plugin is configured')
        else:
            resource_link_id = request.GET.get('resource_link_id', None)

        setattr(request, 'LTI', request.session.get('LTI_LAUNCH', {}).get(resource_link_id, {}))
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
            logger.debug('calling the backend %s clean_username with %s' % (backend, username))
            username = backend.clean_username(username)
            logger.debug('cleaned username is %s' % username)
        except AttributeError:  # Backend has no clean_username method.
            pass
        return username
