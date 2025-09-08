import unittest
from unittest import mock
from unittest.mock import patch
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django_auth_lti import middleware
from django_auth_lti.middleware_patched import MultiLTILaunchAuthMiddleware


@patch("django_auth_lti.middleware.logger")
class TestLTIAuthMiddleware(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mw = MultiLTILaunchAuthMiddleware(lambda r: r)
        self.factory = RequestFactory()

    def build_lti_launch_request(self, post_data):
        """
        Utility method that builds a fake lti launch request with custom data.
        """
        # Add message type to post data
        post_data.update(lti_message_type="basic-lti-launch-request")
        # Add resource_link_id to post data
        if "resource_link_id" not in post_data:
            post_data["resource_link_id"] = "test-resource-link-id"

        request = self.factory.post("/fake/lti/launch", post_data)
        request.user = mock.Mock(name="User", spec=get_user_model())
        request.user.is_authenticated = True
        request.session = {}
        return request

    def _make_mock_user(self):
        """Return a mock user object that behaves like an authenticated user."""
        user = mock.Mock(spec=get_user_model())
        user.is_authenticated = True
        user.pk = 1
        user.username = "testuser"
        user.backend = "django.contrib.auth.backends.ModelBackend"
        return user

    @patch("django_auth_lti.middleware.auth")
    def test_roles_merged_with_custom_roles(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains merged set of roles when custom role key is
        defined and values have been passed in.
        """
        mock_auth.authenticate.return_value = self._make_mock_user()

        request = self.build_lti_launch_request(
            {
                "roles": "RoleOne,RoleTwo",
                "test_custom_role_key": "My,Custom,Roles",
            }
        )
        with patch.object(
            middleware.settings,
            "LTI_CUSTOM_ROLE_KEY",
            "test_custom_role_key",
            create=True,
        ):
            self.mw.process_request(request)
        self.assertEqual(
            request.LTI.get("roles"),
            ["RoleOne", "RoleTwo", "My", "Custom", "Roles"],
        )

    @patch("django_auth_lti.middleware.auth")
    def test_roles_merge_with_empty_custom_roles(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains original set when custom role key is defined with empty data.
        """
        mock_auth.authenticate.return_value = self._make_mock_user()

        request = self.build_lti_launch_request(
            {
                "roles": "RoleOne,RoleTwo",
                "test_custom_role_key": "",
            }
        )
        with patch.object(
            middleware.settings,
            "LTI_CUSTOM_ROLE_KEY",
            "test_custom_role_key",
            create=True,
        ):
            self.mw.process_request(request)
        self.assertEqual(request.LTI.get("roles"), ["RoleOne", "RoleTwo"])

    @patch("django_auth_lti.middleware.auth")
    def test_roles_not_merged_with_no_role_key(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains original set when no custom role key is defined.
        """
        mock_auth.authenticate.return_value = self._make_mock_user()

        request = self.build_lti_launch_request(
            {
                "roles": "RoleOne,RoleTwo",
                "test_custom_role_key": "My,Custom,Roles",
            }
        )
        self.mw.process_request(request)
        self.assertEqual(request.LTI.get("roles"), ["RoleOne", "RoleTwo"])
