from django.urls import path

from .views import InstagramView


app_name = 'basic'
urlpatterns = [
    path('instagram/', InstagramView.as_view()),
]
