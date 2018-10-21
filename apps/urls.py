""" Main paths """

from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from apps.views import MainView


urlpatterns = [
    # Main View
    path('', MainView.as_view(), name='main'),

    # Apps views
    path('basic/', include('apps.basic.urls')),
    path('users/', include('apps.account.urls')),
    path('recipes/', include('apps.recipe.urls')),
    path('stories/', include('apps.story.urls')),
    path('comments/', include('apps.comment.urls')),

    # Auth view
    path('auth/obtain-token/', obtain_jwt_token),
    path('auth/refresh-token/', refresh_jwt_token),
]
