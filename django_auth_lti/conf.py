from django.conf import settings


def get_excluded_paths():
    excluded = getattr(settings, "DJANGO_AUTH_LTI_EXCLUDE_PATHS", [])
    excluded.append("")
    # add a blank path to the list by default, as `path` can sometimes not
    # exist, e.g. when rendering django-debug-toolbar templates
    return excluded
