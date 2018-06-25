""" Main paths """

from django.urls import path

from apps.views import MainView


urlpatterns = [
    path('', MainView.as_view(), name='main'),
]
