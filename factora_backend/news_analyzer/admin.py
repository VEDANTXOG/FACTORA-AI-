from django.contrib import admin
from .models import NewsAnalysis

@admin.register(NewsAnalysis)
class NewsAnalysisAdmin(admin.ModelAdmin):
    list_display = ('news_id', 'verdict', 'manipulation_score', 'verification_score', 'created_at')
    list_filter = ('verdict', 'created_at')
    search_fields = ('news_id', 'uid', 'content')
    readonly_fields = ('news_id', 'uid', 'created_at')
