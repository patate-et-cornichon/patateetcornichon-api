from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site

from .models import Recipe


class RecipeSitemap(Sitemap):
    """ Generate sitemap for recipes."""

    changefreq = 'daily'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Recipe.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return '/recettes/' + obj.slug

    def get_urls(self, site=None, **kwargs):
        """ Set URLs for Patate & Cornichon website """
        if not settings.DEBUG:
            site = Site(
                domain=settings.PATATE_ET_CORNICHON_DOMAIN,
                name=settings.PATATE_ET_CORNICHON_DOMAIN,
            )
        return super().get_urls(site=site, **kwargs)
