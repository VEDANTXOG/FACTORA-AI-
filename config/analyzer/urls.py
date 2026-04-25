from django.urls import path
from .views import analyze_news_view

urlpatterns = [
    path("analyze/", analyze_news_view, name="analyze-news"),
]
