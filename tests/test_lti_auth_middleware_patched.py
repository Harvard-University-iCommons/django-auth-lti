import unittest
from unittest.mock import Mock, PropertyMock, patch

from django_auth_lti.middleware_patched import MultiLTILaunchAuthMiddleware
from django.test import override_settings, RequestFactory

from . import helpers

LTI_AUTH_MAX_LAUNCHES=3

@patch('django_auth_lti.middleware.logger')
class TestLTIAuthMiddleware(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mw = MultiLTILaunchAuthMiddleware()

    def build_lti_launch_request(self, post_data):
        return helpers.build_lti_launch_request(post_data)

    @override_settings(DJANGO_AUTH_LTI_EXCLUDE_PATHS=['/skip_lti/'])
    @patch('django_auth_lti.middleware_patched.auth')
    def test_exclude_path(self, mock_auth, mock_logger):
        """
        Skip LTI session processing if `request.path` is excluded by project settings
        """
        request = RequestFactory().get('/skip_lti/')
        self.mw.process_request(request)
        self.assertIsNone(getattr(request, 'LTI', None))
        self.assertEqual(mock_auth.login.call_count, 0)

    @patch('django_auth_lti.middleware_patched.auth')
    def test_exclude_blank_path(self, mock_auth, mock_logger):
        """
        Skip LTI session processing if `request.path` is blank, as is the case with some
        local requests, like those initiated by the django-debug-toolbar library
        """
        mock_request = Mock(request=Mock(path=''))
        mock_request_LTI_attribute_mock = PropertyMock()
        type(mock_request).LTI = mock_request_LTI_attribute_mock
        self.mw.process_request(mock_request)
        self.assertEqual(mock_request.LTI.call_count, 0)
        self.assertEqual(mock_auth.login.call_count, 0)

    @override_settings(LTI_AUTH_MAX_LAUNCHES=LTI_AUTH_MAX_LAUNCHES)
    @patch('django_auth_lti.middleware_patched.auth')
    @patch('django_auth_lti.middleware_patched.set_current_request')
    def test_lti_multi_launch(self, mock_set_current_request, mock_auth, mock_logger):
        """
        Asserts that multiple LTI launches are maintained in the session.
        """
        mock_auth.authenticate.return_value = True
        session = dict()
        resource_link_ids = ('abc123', 'def456')
        for resource_link_id in resource_link_ids:
            request = self.build_lti_launch_request({"resource_link_id": resource_link_id})
            request.session = session
            self.mw.process_request(request)
            session = request.session  # persist the session across requests

        self.assertIn('LTI_LAUNCH', session)
        self.assertIsInstance(session['LTI_LAUNCH'], dict)
        self.assertEqual(len(resource_link_ids), len(list(session['LTI_LAUNCH'].keys())))
        for resource_link_id in resource_link_ids:
            self.assertIn(resource_link_id, session['LTI_LAUNCH'])
            self.assertEqual(resource_link_id, request.session['LTI_LAUNCH'][resource_link_id]["resource_link_id"])


    @override_settings(LTI_AUTH_MAX_LAUNCHES=LTI_AUTH_MAX_LAUNCHES)
    @patch('django_auth_lti.middleware_patched.auth')
    @patch('django_auth_lti.middleware_patched.set_current_request')
    def test_lti_exceeds_max_launches(self, mock_set_current_request, mock_auth, mock_logger):
        """
        Asserts the constraint for maximum number of LTI launches.
        """
        mock_auth.authenticate.return_value = True
        session = dict()
        resource_link_ids = []
        total_launches = LTI_AUTH_MAX_LAUNCHES + 2
        for i in range(total_launches):
            launch_count = i + 1
            resource_link_id = 'a312fb112a14f9' + str(i)
            resource_link_ids.append(resource_link_id)

            request = self.build_lti_launch_request({"resource_link_id": resource_link_id})
            request.session = session
            self.mw.process_request(request)

            self.assertIn('LTI_LAUNCH_COUNT', request.session)
            self.assertIn('LTI_LAUNCH', request.session)
            self.assertIn(resource_link_id, request.session['LTI_LAUNCH'])
            self.assertEqual(launch_count, request.session['LTI_LAUNCH'][resource_link_id]["_order"])
            self.assertEqual(launch_count, request.session['LTI_LAUNCH_COUNT'])
            self.assertLessEqual(len(list(request.session['LTI_LAUNCH'].keys())), request.session['LTI_LAUNCH_COUNT'])
            self.assertLessEqual(len(list(request.session['LTI_LAUNCH'].keys())), LTI_AUTH_MAX_LAUNCHES)
            session = request.session # persist the session across requests

        # Check that the oldest launches were invalidated
        for i in range(total_launches - LTI_AUTH_MAX_LAUNCHES):
            self.assertNotIn(resource_link_ids[i], session['LTI_LAUNCH'])


    @override_settings(LTI_AUTH_MAX_LAUNCHES=LTI_AUTH_MAX_LAUNCHES)
    @patch('django_auth_lti.middleware_patched.auth')
    @patch('django_auth_lti.middleware_patched.set_current_request')
    def test_lti_relaunch(self, mock_set_current_request, mock_auth, mock_logger):
        """
        Asserts that the same tool relaunched will only occupy one slot.
        """
        mock_auth.authenticate.return_value = True
        session = dict()
        resource_link_id = 'a312fb112a14f9'
        total_launches = LTI_AUTH_MAX_LAUNCHES + 2
        for i in range(total_launches):
            request = self.build_lti_launch_request({"resource_link_id": resource_link_id})
            request.session = session
            self.mw.process_request(request)
            session = request.session  # persist the session across requests

        self.assertIn('LTI_LAUNCH_COUNT', session)
        self.assertIn('LTI_LAUNCH', session)
        self.assertIn(resource_link_id, session['LTI_LAUNCH'])
        self.assertEqual(1, len(list(session['LTI_LAUNCH'].keys())))
        self.assertLessEqual(total_launches, session['LTI_LAUNCH_COUNT'])
