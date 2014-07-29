#!/usr/bin/env python

from django.conf import settings


def runtests():
    settings.configure(
        # App-specific setttings here
    )
    # settings must be configured for this import to work
    from django.test.runner import DiscoverRunner
    DiscoverRunner(interactive=False, failfast=False).run_tests(['django_auth_lti'])

if __name__ == '__main__':
    runtests()
