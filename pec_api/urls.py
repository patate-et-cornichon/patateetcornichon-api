""" Definition origins of URLS. """

from django.urls import include, path


urlpatterns = [
    path('', include('apps.urls')),
]
