from django.test import RequestFactory
from django.contrib.auth import models
from unittest import mock

def build_lti_launch_request(post_data):
    """
    Utility method that builds a fake lti launch request with custom data.
    """
    # Add message type to post data
    post_data.update(lti_message_type='basic-lti-launch-request')
    # Add resource_link_id to post data
    if 'resource_link_id' not in post_data:
        post_data.update(resource_link_id='d202fb112a14f27107149ed874bf630aa8e029a5')

    request = RequestFactory().post('/fake/lti/launch', post_data)
    request.user = mock.Mock(name='User', spec=models.User)
    request.session = {}
    return request
