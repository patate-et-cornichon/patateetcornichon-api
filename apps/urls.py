""" Main paths """

from django.urls import include, path

from apps.views import MainView


urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('users', include('apps.account.urls')),
]
