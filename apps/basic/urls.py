from django.urls import path

from .views import ContactView, InstagramView, MailChimpSubscription


app_name = 'basic'
urlpatterns = [
    path('contact/', ContactView.as_view(), name='contact'),
    path('instagram/', InstagramView.as_view(), name='instagram'),
    path('mailchimp/', MailChimpSubscription.as_view(), name='mailchimp'),
]
