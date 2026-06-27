from django.contrib import admin
from django.urls import path
from django.urls import path
from .views import signup, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/analyze/', 'analyze_news', name='analyze_news'),
    path('api/health/', 'home', name='health_check'),
    path('analyze/', 'analyze_news'),
    path('saved-articles/', 'get_saved_articles'),
    path('delete-article/<str:uid>/', 'delete_article'),
    path('', 'home'),
    path('save-article/', 'save_article'),
    path('signup/', signup),
    path('login/', login)
]
