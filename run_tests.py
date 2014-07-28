#!/usr/bin/env python

from django.conf import settings


def runtests():
    settings.configure(
        INSTALLED_APPS=(
            'django_auth_lti',
        ),
        # App-specific setttings
        LTI_CUSTOM_ROLE_KEY='change-me',
    )
    from django.test.runner import DiscoverRunner
    DiscoverRunner(interactive=False, failfast=False).run_tests(['django_auth_lti'])

if __name__ == '__main__':
    runtests()
