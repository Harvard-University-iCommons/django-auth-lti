"""
Monkey-patch django.core.urlresolvers.reverse to add resource_link_id to all URLs
"""
from urlparse import urlparse, urlunparse, parse_qs
from urllib import urlencode

from django.core import urlresolvers

from .thread_local import get_current_request


django_reverse = None


def reverse(*args, **kwargs):
    """
    Call django's reverse function and append the current resource_link_id as a query parameter
    """
    request = get_current_request()
    url = django_reverse(*args, **kwargs)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'resource_link_id' not in query.keys():
        query['resource_link_id'] = request.LTI.get('resource_link_id')
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(query), parsed.fragment))
    return url


def patch_reverse():
    """
    Monkey-patches the django.core.urlresolvers.reverse function. Will not patch twice.
    """
    global django_reverse
    if urlresolvers.reverse is not reverse:
        django_reverse = urlresolvers.reverse
        urlresolvers.reverse = reverse


patch_reverse()
