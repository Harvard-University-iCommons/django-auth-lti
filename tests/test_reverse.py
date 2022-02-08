from unittest import TestCase
from unittest.mock import patch

from django.test import override_settings, RequestFactory
from django.urls import reverse

from . import helpers
from django_auth_lti.middleware_patched import MultiLTILaunchAuthMiddleware

class TestReverse(TestCase):
    def setUp(self):
        self.mw = MultiLTILaunchAuthMiddleware()

    def build_lti_launch_request(self, post_data, url):
        return helpers.build_lti_launch_request(post_data, url)

    @patch('django_auth_lti.middleware.logger')
    @patch('django_auth_lti.middleware_patched.auth')
    def test_patched_reverse_adds_resource_link_id(self, mock_auth, mock_logger):
        """
        `django.urls.reverse()` should add the `resource_link_id` from the LTI session to the URL
        (`django.urls.reverse` should be patched automatically by importing MultiLTILaunchAuthMiddleware)
        """
        mock_auth.authenticate.return_value = True
        request = self.build_lti_launch_request({"resource_link_id": 'abc123'}, url='/lti_launch/')
        self.mw.process_request(request)
        url = reverse('lti_launch')
        self.assertEqual(url, '/lti_launch/?resource_link_id=abc123')

    @override_settings(DJANGO_AUTH_LTI_EXCLUDE_PATHS=['/skip_lti/'])
    @patch('django_auth_lti.middleware.logger')
    @patch('django_auth_lti.middleware_patched.auth')
    def test_patched_reverse_exclude_paths_settings(self, mock_auth, mock_logger):
        """
        `django.urls.reverse()` should not check the LTI session for the `resource_link_id` if the `request.path` is excluded by project settings
        (`django.urls.reverse` should be patched automatically by importing MultiLTILaunchAuthMiddleware)
        """
        mock_auth.authenticate.return_value = True
        request = RequestFactory().get('/skip_lti/')
        self.mw.process_request(request)
        url = reverse('lti_launch')
        self.assertEqual(url, '/lti_launch/')

    @patch('django_auth_lti.middleware.logger')
    @patch('django_auth_lti.middleware_patched.auth')
    def test_patched_reverse_exclude_resource_link_id_param(self, mock_auth, mock_logger):
        """
        `django.urls.reverse()` should not check the LTI session for the `resource_link_id` if the `exclude_resource_link_id` is set to `True` when called
        (`django.urls.reverse` should be patched automatically by importing MultiLTILaunchAuthMiddleware)
        """
        mock_auth.authenticate.return_value = True
        request = self.build_lti_launch_request({"resource_link_id": 'abc123'}, url='/lti_launch/')
        self.mw.process_request(request)
        url = reverse('lti_launch', exclude_resource_link_id=True)
        self.assertEqual(url, '/lti_launch/')
