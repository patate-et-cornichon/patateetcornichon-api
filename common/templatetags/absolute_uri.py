from django import template
from django.templatetags import static


register = template.Library()


class AbsoluteUriStaticNode(static.StaticNode):
    """ Override the default static node in order to return an absolute uri. """
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))


@register.tag('absolute_uri_static')
def do_absolute_uri_static(parser, token):
    return AbsoluteUriStaticNode.handle_token(parser, token)
