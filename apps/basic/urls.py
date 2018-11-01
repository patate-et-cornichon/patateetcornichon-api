from django.urls import path

from .views import ContactView, InstagramView, MailChimpSubscription


app_name = 'basic'
urlpatterns = [
    path('contact/', ContactView.as_view()),
    path('instagram/', InstagramView.as_view()),
    path('mailchimp/', MailChimpSubscription.as_view()),
]
