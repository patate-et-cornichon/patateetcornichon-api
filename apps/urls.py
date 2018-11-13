""" Main paths """
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.cache import cache_page
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from apps.recipe.sitemap import RecipeSitemap
from apps.story.sitemap import StorySitemap
from apps.views import MainView


sitemaps = {
    'story': StorySitemap,
    'recipe': RecipeSitemap,
}

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

    # Sitemaps
    path(
        'sitemap.xml/',
        cache_page(86400)(sitemap),
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path(
        'sitemap-<section>.xml/',
        cache_page(86400)(sitemap),
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
]
