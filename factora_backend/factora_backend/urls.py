from django.contrib import admin
from django.urls import path
from news_analyzer.views_fixed import analyze_news, home, get_saved_articles, delete_article, save_article, get_article_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze/', analyze_news),
    path('saved-articles/', get_saved_articles),
    path('delete-article/<str:uid>/', delete_article),
    path('', home),   # 👈 ADD THIS LINE
    path('save-article/', save_article),
    path('article/<str:uid>/', get_article_detail),
]

