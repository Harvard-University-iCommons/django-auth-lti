"""
Monkey-patch django.core.urlresolvers.reverse to add resource_link_id to all URLs
"""
import logging
from urlparse import urlparse, urlunparse, parse_qs
from urllib import urlencode

# Django 1.10 moved urlresolvers into django.urls package
try:
    from django import urls as urlresolvers
except ImportError:
    from django.core import urlresolvers

from .thread_local import get_current_request

logger = logging.getLogger(__name__)

django_reverse = None


def reverse(*args, **kwargs):
    """
    Call django's reverse function and append the current resource_link_id as a query parameter

    :param kwargs['exclude_resource_link_id']: Do not add the resource link id as a query parameter
    :returns Django named url
    """
    logger.debug("inside custom reverse function!")
    request = get_current_request()

    # Check for custom exclude_resource_link_id kwarg and remove it before passing kwargs to django reverse
    exclude_resource_link_id = kwargs.pop('exclude_resource_link_id', False)

    url = django_reverse(*args, **kwargs)
    if not exclude_resource_link_id:
        # Append resource_link_id query param if exclude_resource_link_id kwarg was not passed or is False
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'resource_link_id' not in query.keys():
            query['resource_link_id'] = request.LTI.get('resource_link_id')
            url = urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(query), parsed.fragment)
            )
    return url


def patch_reverse():
    """
    Monkey-patches the reverse function. Will not patch twice.
    """
    global django_reverse
    if urlresolvers.reverse is not reverse:
        logger.debug("inside patch_reverse where urlresolvers.reverse != reverse")
        django_reverse = urlresolvers.reverse
        urlresolvers.reverse = reverse


patch_reverse()
