from django.urls import path
from django.views.generic import TemplateView


app_name = 'test_app'
urlpatterns = [
    path(r'lti_launch/', TemplateView.as_view(), name='lti_launch'),
]
