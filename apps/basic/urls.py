from django.urls import path

from .views import InstagramView, MailChimpSubscription


app_name = 'basic'
urlpatterns = [
    path('instagram/', InstagramView.as_view()),
    path('mailchimp/', MailChimpSubscription.as_view()),
]
