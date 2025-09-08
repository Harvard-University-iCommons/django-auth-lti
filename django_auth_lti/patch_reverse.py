"""
Monkey-patch django's reverse function to add resource_link_id to all URLs.
"""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import django.shortcuts
import django.urls

from django_auth_lti.conf import get_excluded_paths

from .thread_local import get_current_request

_original_reverse = django.urls.reverse


def reverse(*args, **kwargs):
    """
    Call django's reverse function and append the current resource_link_id as a
    query parameter

    :param kwargs['exclude_resource_link_id']: Do not add the resource link id
    as a query parameter
    :returns Django named url
    """
    request = get_current_request()

    # Check for custom exclude_resource_link_id kwarg and remove it before
    # passing kwargs to django reverse
    exclude_resource_link_id = kwargs.pop("exclude_resource_link_id", False)
    excluded_path = getattr(request, "path", "") in get_excluded_paths()

    url = _original_reverse(*args, **kwargs)

    if request and not exclude_resource_link_id and not excluded_path:
        # Append resource_link_id query param if exclude_resource_link_id kwarg
        # was not passed or is False
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        if "resource_link_id" not in query and getattr(request, "LTI", None):
            resource_link_id = request.LTI.get("resource_link_id")
            if resource_link_id:
                query["resource_link_id"] = resource_link_id
                url = urlunparse(
                    (
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        urlencode(query, doseq=True),
                        parsed.fragment,
                    )
                )
    return url


def patch_reverse():
    # """
    # Monkey-patches the reverse function. Will not patch twice.
    # """
    # global django_reverse
    # from django import urls

    # if urls.reverse is not reverse:
    #     django_reverse = urls.reverse
    #     urls.reverse = reverse

    #     # Django 1.10 moves url helper functions like `reverse` into a new urls
    #     # module, so we need to patch it as well.  In addition, the
    #     # django.shortcuts module now includes `reverse` directly, and the
    #     # module appears to be loaded before middleware so we need to
    #     # retroactively patch that `reverse` reference as well.
    #     try:
    #         from django import urls, shortcuts

    #         urls.reverse = reverse
    #         shortcuts.reverse = reverse
    #     except ImportError:
    #         pass
    """Monkey-patch reverse in Django modules if not already patched."""
    if django.urls.reverse is not reverse:
        django.urls.reverse = reverse
        django.shortcuts.reverse = reverse


patch_reverse()
